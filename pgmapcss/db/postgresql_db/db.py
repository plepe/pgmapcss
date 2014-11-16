from ..default import default
import pgmapcss.db.pg

# This class is the base class for all database using a postgresql database
class postgresql_db(default):
    def __init__(self, conn, stat):
        default.__init__(self, conn, stat)
        self.format = pgmapcss.db.pg.format
        self.ident = pgmapcss.db.pg.ident

    def merge_conditions(self, conditions):
        conditions = set(conditions)
        types = [ t for t, cs in conditions if t != True ]

        conditions = {
            t:
                '(' + ') or ('.join([
                    cs
                    for t2, cs in conditions
                    if t == t2
                    if cs != 'false'
                ]) + ')'
            for t in types
        }

        return {
            t: cs
            for t, cs in conditions.items()
            if cs != '()'
        }

    def compile_condition_hstore_value(self, condition, statement, tag_type, stat, prefix, filter):
        ret = None
        negate = False
        key = tag_type[1]
        column = tag_type[2]
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
            ret = prefix + column + ' ? ' + self.format(key);

        # =
        elif op == '=':
            ret = prefix + column + ' @> ' + self.format({ key: condition['value'] })

        # @=
        elif op == '@=' and condition['value_type'] == 'value':
            ret = '(' + ' or '.join([
                prefix + column + ' @> ' + self.format({ key: v })
                for v in condition['value'].split(';')
                ]) + ')'

        # !=
        elif op == '!=':
            ret = '( not ' + prefix + column + ' ? ' + self.format(key) +\
                   'or not ' + prefix + column + ' @> ' +\
                   self.format({ key: condition['value'] }) + ')'

        # regexp match =~
        elif op == '=~':
            ret = '(' + prefix + column + ' ? ' + self.format(key) + ' and ' +\
                prefix + column + '->' + self.format(key) +\
                (' ~* ' if 'i' in condition['regexp_flags'] else ' ~ ') +\
                self.format(condition['value']) + ')'

        # negated regexp match !~
        elif op == '!~':
            ret = '(' + prefix + column + ' ? ' + self.format(key) + ' and ' +\
                prefix + column + '->' + self.format(key) +\
                (' !~* ' if 'i' in condition['regexp_flags'] else ' !~ ') +\
                self.format(condition['value']) + ')'

        # prefix match ^=
        elif op == '^=':
            ret = '(' + prefix + column + ' ? ' + self.format(key) + ' and ' +\
                prefix + column + '->' + self.format(key) + ' like ' +\
                self.format(self.pg_like_escape(condition['value']) + '%') + ')'

        # suffix match $=
        elif op == '$=':
            ret = '(' + prefix + column + ' ? ' + self.format(key) + ' and ' +\
                prefix + column + '->' + self.format(key) + ' like ' +\
                self.format('%' + self.pg_like_escape(condition['value'])) + ')'

        # substring match *=
        elif op == '*=':
            ret = '(' + prefix + column + ' ? ' + self.format(key) + ' and ' +\
                prefix + column + '->' + self.format(key) + ' like ' +\
                self.format('%' + self.pg_like_escape(condition['value']) + '%') + ')'

        # list membership ~=
        elif op == '~=':
            ret = '(' + prefix + column + ' ? ' + self.format(key) + ' and ' +\
                self.format(condition['value']) + ' =any(string_to_array(' +\
                prefix + column + '->' + self.format(key) + ', \';\')))'

        else:
            ret = prefix + column + ' ? ' + self.format(key)

        if ret is None:
            return None

        if negate:
            return '(not ' + prefix + column + ' ? ' + self.format(key) +\
                ' or not ' + ret + ')'

        return ret

    def compile_condition_column(self, condition, statement, tag_type, stat, prefix, filter):
        ret = None
        key = tag_type[1]
        op = condition['op']
        negate = False

        value_format = self.value_format_default
        if len(tag_type) > 2:
            value_format = tag_type[2]

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
            ret = prefix + self.ident(key) + ' is not null'

        # =
        elif op == '=':
            # if value_format returns None -> can't resolve, discard condition
            # if value_format returns False -> return false as result
            f = value_format(key, condition['value'])
            if f is None:
                return None
            elif f:
                ret = prefix + self.ident(key) + ' = ' + f
            else:
                ret = 'false'

        # @=
        elif op == '@=' and condition['value_type'] == 'value':
            f = {
                value_format(key, v)
                for v in condition['value'].split(';')
            }
            # if value_format returns None -> can't resolve, discard condition
            # if value_format returns False -> return false as result
            if None in f:
                return None
            if False in f:
                f.remove(None)

            if len(f):
                ret = prefix + self.ident(key) + ' in (' + ', '.join(f) + ')'
            else:
                ret = 'false'

        # !=
        elif op == '!=':
            ret = '(' + prefix + self.ident(key) + 'is null or ' +\
                prefix + self.ident(key) + '!=' +\
                self.format(condition['value']) + ')'

        # regexp match =~
        elif op == '=~':
            ret = prefix + self.ident(key) +\
                (' ~* ' if 'i' in condition['regexp_flags'] else ' ~ ') +\
                self.format(condition['value'])

        # negated regexp match !~
        elif op == '!~':
            ret = prefix + self.ident(key) +\
                (' !~* ' if 'i' in condition['regexp_flags'] else ' !~ ') +\
                self.format(condition['value'])

        # prefix match ^=
        elif op == '^=':
            ret = prefix + self.ident(key) + ' like ' +\
                self.format(self.pg_like_escape(condition['value']) + '%')

        # suffix match $=
        elif op == '$=':
            ret = prefix + self.ident(key) + ' like ' +\
                self.format('%' + self.pg_like_escape(condition['value']))

        # substring match *=
        elif op == '*=':
            ret = prefix + self.ident(key) + ' like ' +\
                self.format('%' + self.pg_like_escape(condition['value']) + '%')

        # list membership ~=
        elif op == '~=':
            ret = \
                self.format(condition['value']) + ' =any(string_to_array(' +\
                prefix + self.ident(key) + ', \';\'))'

        else:
            ret = prefix + self.ident(key) + ' is not null'

        if ret is None:
            return None

        if negate:
            return '(' + prefix + self.ident(key) + ' is null or not ' + ret + ')'

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
            ret.add('((' + ') or ('.join([
                self.compile_selector(s, stat, prefix, filter)
                for s in set_statements
            ]) + '))')

        # ignore generated tags (identified by leading .)
        if condition['key'][0] == '.':
            if len(ret) == 0:
                return 'false'
            return ''.join(ret)

        # depending on the tag type compile the specified condition
        tag_type = stat['database'].tag_type(condition['key'], condition, statement['selector'], statement)

        if tag_type is None:
            pass
        elif tag_type[0] == 'hstore-value':
            ret.add(self.compile_condition_hstore_value(condition, statement, tag_type, stat, prefix, filter))
        elif tag_type[0] == 'column':
            ret.add(self.compile_condition_column(condition, statement, tag_type, stat, prefix, filter))
        else:
            raise CompileError('unknown tag type {}'.format(tag_type))

        if None in ret:
            ret.remove(None)
        if len(ret) == 0:
            return None

        # merge conditions together, return
        return '(' + ' or '.join(ret) + ')'    

    def compile_selector(self, statement, stat, prefix='current.', filter={}, object_type=None):
        filter['object_type'] = object_type

        ret = {
            self.compile_condition(c, statement, stat, prefix, filter) or 'true'
            for c in statement['selector']['conditions']
        }

        if len(ret) == 0:
            return 'true'

        if 'false' in ret:
            return 'false'

        return ' and '.join(ret)

    def value_format_default(self, key, value):
        return self.format(value)

    # escape strings for "like" matches, see http://www.postgresql.org/docs/9.1/static/functions-matching.html
    def pg_like_escape(self, s):
        s = s.replace('\\', '\\\\')
        s = s.replace('_', '\\_')
        s = s.replace('%', '\\%')
        return s
