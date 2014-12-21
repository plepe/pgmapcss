from pkg_resources import *
import postgresql
from ..default import default
from ..pg import format
from ..pg import ident

class db(default):
    def __init__(self, conn, stat):
        default.__init__(self, conn, stat)
        if not 'db.srs' in self.stat['config']:
            self.stat['config']['db.srs'] = 4326

        if not 'db.overpass-url' in self.stat['config']:
            self.stat['config']['db.overpass-url'] = 'http://overpass-api.de/api'

    def tag_type(self, key, condition):
        if key[0:4] == 'osm:':
            return None

        return ( 'overpass', key )

    def value_to_regexp(self, s):
        s = s.replace('\\', '\\\\')
        s = s.replace('.', '\\.')
        s = s.replace('|', '\\|')
        s = s.replace('[', '\\[')
        s = s.replace(']', '\\]')
        s = s.replace('(', '\\(')
        s = s.replace(')', '\\)')
        s = s.replace('{', '\\{')
        s = s.replace('}', '\\}')
        s = s.replace('?', '\\?')
        s = s.replace('+', '\\+')
        s = s.replace('*', '\\*')
        s = s.replace('^', '\\^')
        s = s.replace('$', '\\$')
        return s

    def convert_to_regexp(self, s):
        if s[0] in ('regexp', 'iregexp', 'isnot', 'notregexp', 'notiregexp'):
            return s
        if s[0] == 'is':
            return ('regexp', s[1], { '^' + self.value_to_regexp(s[2]) + '$' })

    def compile_condition_overpass(self, condition, tag_type, filter):
        ret = None
        negate = False
        key = tag_type[1]
        op = condition['op']

        if op[0:2] == '! ':
            op = op[2:]
            negate = True

        # eval() statements
        if op == 'eval':
            return None

        # ignore pseudo classes
        if op == 'pseudo_class':
            return None

        # regexp on key of tag
        if op in ('key_regexp', 'key_regexp_case'):
            return None

        # value-eval() statements
        if condition['value_type'] == 'eval':
            # treat other conditions as has_key
            ret = ( 'key', key )

        # =
        elif op == '=':
            #ret = ( 'is', key, condition['value'] )
            ret = ( 'regexp', key, { '^' + self.value_to_regexp(condition['value']) + '$' })

        # @=
        elif op == '@=' and condition['value_type'] == 'value':
            ret = ( 'regexp', key, {
                '^' + self.value_to_regexp(v) + '$'
                for v in condition['value'].split(';')
                } )

        # !=
        elif op == '!=':
            #ret = ( 'isnot', key, condition['value'] )
            ret = ( 'notregexp', key, { '^' + self.value_to_regexp(condition['value']) + '$' })

        # regexp match =~
        elif op == '=~':
            ret = (
                ('iregexp' if condition['regexp_flags'] else 'regexp' ),
                key, { condition['value'] })

        # negated regexp match !~
        elif op == '!~':
            ret = ( 
                ('notiregexp' if condition['regexp_flags'] else 'notregexp' ),
                key, { condition['value'] })

        # prefix match ^=
        elif op == '^=':
            ret = ( 'regexp', key, { '^' + self.value_to_regexp(condition['value']) } )

        # suffix match $=
        elif op == '$=':
            ret = ( 'regexp', key, { self.value_to_regexp(condition['value']) + '$' } )

        # substring match *=
        elif op == '*=':
            ret = ( 'regexp', key, { self.value_to_regexp(condition['value']) })

        # list membership ~=
        elif op == '~=':
            ret = ( 'regexp', key, { self.value_to_regexp(condition['value']) })

        else:
            ret = ( 'key', key )

        if ret is None:
            return None

        if negate:
            return None # TODO
#            return '(not ' + prefix + column + ' ? ' + db.format(key) +\
#                ' or not ' + ret + ')'

        return ret

    # returns None if it's not possible to query for condition (e.g. osm:user)
    # returns False if query always evaluates negative
    def compile_condition(self, condition, filter={}):
        ret = []

        # depending on the tag type compile the specified condition
        tag_type = self.stat['database'].tag_type(condition['key'], condition)

        if tag_type is None:
            pass
        elif tag_type[0] == 'overpass':
            ret = self.compile_condition_overpass(condition, tag_type, filter)
        else:
            raise CompileError('unknown tag type {}'.format(tag_type))

        # return
        return ret

    def conditions_to_query(self, conditions):
        ret = '__TYPE__';

        for c in conditions:
            if c[0] == 'type':
                pass
            elif c[0] == 'key':
                ret += '[' + repr(c[1]) + ']'
            elif c[0] == 'is':
                ret += '[' + repr(c[1]) + '=' + repr(c[2]) + ']'
            elif c[0] == 'isnot':
                ret += '[' + repr(c[1]) + '!=' + repr(c[2]) + ']'
            elif c[0] == 'regexp':
                ret += '[' + repr(c[1]) + '~' + self.merge_regexp(c[2]) + ']'
            elif c[0] == 'iregexp':
                ret += '[' + repr(c[1]) + '~' + self.merge_regexp(c[2]) + ', i]'
            elif c[0] == 'notregexp':
                ret += '[' + repr(c[1]) + '!~' + self.merge_regexp(c[2]) + ']'
            elif c[0] == 'notiregexp':
                ret += '[' + repr(c[1]) + '!~' + self.merge_regexp(c[2]) + ', i]'
            else:
                print('Unknown Overpass operator "{}"'.format(c[0]))

        return ret

    def merge_regexp(self, regexps):
        r = ''
        r_end = ''

        if len([ r for r in regexps if r[0] == '^' ]):
            r += '^'
            regexps = {
                    r[1:] if r[0] == '^' else '.*' + r
                    for r in regexps
                }

        if len([ r for r in regexps if r[-1] == '$' ]):
            r_end = '$'
            regexps = {
                    r[:-1] if r[-1] == '$' else r + '.*'
                    for r in regexps
                }

        return repr(r + '|'.join(regexps) + r_end)

    def is_subset(self, c1, c2):
        # check if query c1 is a subset of query c2 -> replace by c1
        if len([ e1 for e1 in c1 if e1 not in c2 ]) == 0:
            return c1

        # c1 and c2 only differ in one condition and it has the same key
        d1 = [ e1 for e1 in c1 if e1 not in c2 ]
        d2 = [ e2 for e2 in c2 if e2 not in c1 ]
        if len(d1) == 1 and len(d2) == 1 and d1[0][1] == d2[0][1]:
            # one of the differing conditions queries for key -> ignore other condition
            if d1[0][0] == 'key' or d2[0][0] == 'key':
                return [
                        c
                        for c in c1
                        if c != d1[0]
                    ] + [ ( 'key', d1[0][1] ) ]

    def check_merge_regexp(self, c1, c2):
        # c1 and c2 only differ in one condition and it has the same key
        d1 = [ e1 for e1 in c1 if e1 not in c2 ]
        d2 = [ e2 for e2 in c2 if e2 not in c1 ]
        if len(d1) == 1 and len(d2) == 1 and d1[0][1] == d2[0][1]:
            # check if we can merge the regular expressions
            m1 = self.convert_to_regexp(d1[0])
            m2 = self.convert_to_regexp(d2[0])

            if m1[0] == m2[0]:
                return [
                        c
                        for c in c1
                        if c != d1[0]
                    ] + [ ( m1[0], d1[0][1], m1[2].union(m2[2]) ) ]

    def simplify_conditions(self, conditions):
        for i1 in range(0, len(conditions)):
            for i2 in range(0, len(conditions)):
                c1 = conditions[i1]
                c2 = conditions[i2]

                if i1 != i2 and c1 is not None and c2 is not None:
                    s = self.is_subset(c1, c2)
                    if s is not None:
                        conditions[i1] = s
                        conditions[i2] = None

        conditions = [ c for c in conditions if c is not None ]

        for i1 in range(0, len(conditions)):
            for i2 in range(0, len(conditions)):
                c1 = conditions[i1]
                c2 = conditions[i2]

                if i1 != i2 and c1 is not None and c2 is not None:
                    s = self.check_merge_regexp(c1, c2)
                    if s is not None:
                        conditions[i1] = s
                        conditions[i2] = None

        conditions = [ c for c in conditions if c is not None ]

        return conditions

    def merge_conditions(self, conditions):
        conditions = [
                c
                for cs in conditions
                for c in cs
            ]

        conditions = self.simplify_conditions(conditions)

        if len(conditions) == 0:
            return False

        return ';\n'.join([
                self.conditions_to_query(c)
                for c in conditions
            ]) + ';\n'

    def compile_selector(self, selector, no_object_type=False):
        filter = {}
        filter['object_type'] = selector['type']

        conditions = [
            self.compile_condition(c, filter)
            for c in selector['conditions']
        ]

        ret = [ [] ]

        for condition in conditions:
            if condition is None:
                continue

            elif type(condition) == list:
                ret = [
                    r + c
                    for r in ret
                    for cs in condition
                    for c in cs
                ]

            elif type(condition) == tuple:
                ret = [
                        r + [ condition ]
                        for r in ret
                    ]

            elif condition == False:
                return False

        if no_object_type:
            return ret

        return ret
