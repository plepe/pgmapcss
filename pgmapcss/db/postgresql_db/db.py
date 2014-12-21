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

        conditions = '(' + ') or ('.join([
                cs
                for cs in conditions
                if cs != 'false'
            ]) + ')'

        if conditions == '()':
            return False

        return conditions

    def compile_condition_hstore_value(self, condition, tag_type, filter):
        ret = None
        negate = False
        key = tag_type[1]
        column = tag_type[2]
        op = condition['op']
        prefix = ''

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

            if 'db.hstore_key_index' in self.stat['config'] and key in self.stat['config']['db.hstore_key_index']:
                ret += ' and ' + prefix + column + ' ? ' + self.format(key)

        # @=
        elif op == '@=' and condition['value_type'] == 'value':
            ret = '(' + ' or '.join([
                prefix + column + ' @> ' + self.format({ key: v })
                for v in condition['value'].split(';')
                ]) + ')'

            if 'db.hstore_key_index' in self.stat['config'] and key in self.stat['config']['db.hstore_key_index']:
                ret += ' and ' + prefix + column + ' ? ' + self.format(key)

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

    def compile_condition_column(self, condition, tag_type, filter):
        ret = None
        key = tag_type[1]
        op = condition['op']
        negate = False
        prefix = ''

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

    def compile_condition(self, condition, selector, filter={}):
        ret = set()

        # depending on the tag type compile the specified condition
        tag_type = self.stat['database'].tag_type(condition['key'], condition, selector)

        if tag_type is None:
            pass
        elif tag_type[0] == 'hstore-value':
            ret.add(self.compile_condition_hstore_value(condition, tag_type, filter))
        elif tag_type[0] == 'column':
            ret.add(self.compile_condition_column(condition, tag_type, filter))
        else:
            raise CompileError('unknown tag type {}'.format(tag_type))

        if None in ret:
            ret.remove(None)
        if len(ret) == 0:
            return None

        # merge conditions together, return
        return '(' + ' or '.join(ret) + ')'    

    def compile_selector(self, selector):
        filter = {}
        filter['object_type'] = selector['type']

        ret = {
            self.compile_condition(c, selector, filter) or 'true'
            for c in selector['conditions']
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
