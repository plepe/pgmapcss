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
            self.stat['config']['db.overpass-url'] = 'http://overpass-api.de/api/interpreter'

    def tag_type(self, key, condition, selector, statement):
        if key[0:4] == 'osm:':
            if key == 'osm:id':
                return ( 'column', 'id', self.compile_modify_id )
            elif key == 'osm:user':
                return ( 'column', 'user_id', self.compile_user_id )
            elif key == 'osm:user_id':
                return ( 'column', 'user_id' )
            elif key == 'osm:version':
                return ( 'column', 'version' )
            elif key == 'osm:timestamp':
                return ( 'column', 'tstamp' )
            elif key == 'osm:changeset':
                return ( 'column', 'changeset_id' )
            else:
                return None

        return ( 'overpass', key )

    def compile_condition_overpass(self, condition, statement, tag_type, stat, prefix, filter):
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
            ret = prefix + column + ' ? ' + db.format(key);

        # =
        elif op == '=':
            ret = '[' + repr(key) + '=' + repr(condition['value']) + ']'

        # @=
        elif op == '@=' and condition['value_type'] == 'value':
            ret = '(' + ' or '.join([
                prefix + column + ' @> ' + db.format({ key: v })
                for v in condition['value'].split(';')
                ]) + ')'

        # !=
        elif op == '!=':
            ret = '( not ' + prefix + column + ' ? ' + db.format(key) +\
                   'or not ' + prefix + column + ' @> ' +\
                   db.format({ key: condition['value'] }) + ')'

        # regexp match =~
        elif op == '=~':
            ret = '(' + prefix + column + ' ? ' + db.format(key) + ' and ' +\
                prefix + column + '->' + db.format(key) +\
                (' ~* ' if 'i' in condition['regexp_flags'] else ' ~ ') +\
                db.format(condition['value']) + ')'

        # negated regexp match !~
        elif op == '!~':
            ret = '(' + prefix + column + ' ? ' + db.format(key) + ' and ' +\
                prefix + column + '->' + db.format(key) +\
                (' !~* ' if 'i' in condition['regexp_flags'] else ' !~ ') +\
                db.format(condition['value']) + ')'

        # prefix match ^=
        elif op == '^=':
            ret = '(' + prefix + column + ' ? ' + db.format(key) + ' and ' +\
                prefix + column + '->' + db.format(key) + ' like ' +\
                db.format(pg_like_escape(condition['value']) + '%') + ')'

        # suffix match $=
        elif op == '$=':
            ret = '(' + prefix + column + ' ? ' + db.format(key) + ' and ' +\
                prefix + column + '->' + db.format(key) + ' like ' +\
                db.format('%' + pg_like_escape(condition['value'])) + ')'

        # substring match *=
        elif op == '*=':
            ret = '(' + prefix + column + ' ? ' + db.format(key) + ' and ' +\
                prefix + column + '->' + db.format(key) + ' like ' +\
                db.format('%' + pg_like_escape(condition['value']) + '%') + ')'

        # list membership ~=
        elif op == '~=':
            ret = '(' + prefix + column + ' ? ' + db.format(key) + ' and ' +\
                db.format(condition['value']) + ' =any(string_to_array(' +\
                prefix + column + '->' + db.format(key) + ', \';\')))'

        else:
            ret = '[' + repr(key) + ']'

        if ret is None:
            return None

        if negate:
            return '(not ' + prefix + column + ' ? ' + db.format(key) +\
                ' or not ' + ret + ')'

        return ret

    def compile_condition(self, condition, statement, stat, prefix='current.', filter={}):
        ret = set()

        # assignments: map conditions which are based on a (possible) set-statement
        # back to their original selectors:
        f = filter.copy()
        f['has_set_tag'] = condition['key']
        f['max_id'] = statement['id']
        set_statements = stat.filter_statements(f)

        if len(set_statements) > 0:
            set_statements = {
                self.compile_selector(s, stat, prefix, filter, no_object_type=True)
                for s in set_statements
            }

        # ignore generated tags (identified by leading .)
        if condition['key'][0] == '.':
            return set_statements

        # depending on the tag type compile the specified condition
        tag_type = stat['database'].tag_type(condition['key'], condition, statement['selector'], statement)

        if tag_type is None:
            pass
        elif tag_type[0] == 'overpass':
            ret.add(self.compile_condition_overpass(condition, statement, tag_type, stat, prefix, filter))
        else:
            raise CompileError('unknown tag type {}'.format(tag_type))

        if None in ret:
            ret.remove(None)
        if len(ret) == 0:
            return set_statements

        if len(set_statements):
            return {
                    s + ''.join(ret)
                    for s in set_statements
                }

        # merge conditions together, return
        return ''.join(ret)

    def merge_conditions(self, conditions):
        types = [ t for t, cs in conditions if t != True ]

        conditions = {
            t:
                '(\n' + '\n'.join([
                    cs
                    for t2, cs in conditions
                    if t == t2
                    if cs != 'false'
                ]) + '\n);'
            for t in types
        }

        return {
            t: cs
            for t, cs in conditions.items()
            if cs != '()'
        }

    def compile_selector(self, statement, stat, prefix='current.', filter={}, object_type=None, no_object_type=False):
        filter['object_type'] = object_type

        conditions = [
            self.compile_condition(c, statement, stat, prefix, filter) or None
            for c in statement['selector']['conditions']
        ]

        if no_object_type:
            ret = { '' }
        else:
            ret = { '__TYPE__' }

        for condition in conditions:
            if condition is None:
                continue

            if condition is None:
                pass

            elif type(condition) == set:
                ret = [
                        r + c
                        for c in condition
                        for r in ret
                    ]
            else:
                ret = [
                        r + condition
                        for r in ret
                    ]

        if False in ret:
            return False

        if no_object_type:
            return ''.join(ret)

        return ';'.join(ret) + ';'
