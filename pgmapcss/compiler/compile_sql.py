import pgmapcss.db as db
from .CompileError import CompileError

def value_format_default(key, value):
    return db.format(value)

# escape strings for "like" matches, see http://www.postgresql.org/docs/9.1/static/functions-matching.html
def pg_like_escape(s):
    s = s.replace('\\', '\\\\')
    s = s.replace('_', '\\_')
    s = s.replace('%', '\\%')
    return s

def compile_condition_hstore_value(condition, statement, tag_type, stat, prefix, filter):
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
        ret = prefix + column + ' ? ' + db.format(key);

    # =
    elif op == '=':
        print('here')
        ret = prefix + column + ' @> ' + db.format({ key: condition['value'] })

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
        ret = prefix + column + ' ? ' + db.format(key)

    if ret is None:
        return None

    if negate:
        return '(not ' + prefix + column + ' ? ' + db.format(key) +\
            ' or not ' + ret + ')'

    return ret

def compile_condition_column(condition, statement, tag_type, stat, prefix, filter):
    ret = None
    key = tag_type[1]
    op = condition['op']
    negate = False

    value_format = value_format_default
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
        ret = prefix + db.ident(key) + ' is not null'

    # =
    elif op == '=':
        # if value_format returns None -> can't resolve, discard condition
        # if value_format returns False -> return false as result
        f = value_format(key, condition['value'])
        if f is None:
            return None
        elif f:
            ret = prefix + db.ident(key) + ' = ' + f
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
            ret = prefix + db.ident(key) + ' in (' + ', '.join(f) + ')'
        else:
            ret = 'false'

    # !=
    elif op == '!=':
        ret = '(' + prefix + db.ident(key) + 'is null or ' +\
            prefix + db.ident(key) + '!=' +\
            db.format(condition['value']) + ')'

    # regexp match =~
    elif op == '=~':
        ret = prefix + db.ident(key) +\
            (' ~* ' if 'i' in condition['regexp_flags'] else ' ~ ') +\
            db.format(condition['value'])

    # negated regexp match !~
    elif op == '!~':
        ret = prefix + db.ident(key) +\
            (' !~* ' if 'i' in condition['regexp_flags'] else ' !~ ') +\
            db.format(condition['value'])

    # prefix match ^=
    elif op == '^=':
        ret = prefix + db.ident(key) + ' like ' +\
            db.format(pg_like_escape(condition['value']) + '%')

    # suffix match $=
    elif op == '$=':
        ret = prefix + db.ident(key) + ' like ' +\
            db.format('%' + pg_like_escape(condition['value']))

    # substring match *=
    elif op == '*=':
        ret = prefix + db.ident(key) + ' like ' +\
            db.format('%' + pg_like_escape(condition['value']) + '%')

    # list membership ~=
    elif op == '~=':
        ret = \
            db.format(condition['value']) + ' =any(string_to_array(' +\
            prefix + db.ident(key) + ', \';\'))'

    else:
        ret = prefix + db.ident(key) + ' is not null'

    if ret is None:
        return None

    if negate:
        return '(' + prefix + db.ident(key) + ' is null or not ' + ret + ')'

    return ret

def compile_condition_sql(condition, statement, stat, prefix='current.', filter={}):
    ret = set()

    # assignments: map conditions which are based on a (possible) set-statement
    # back to their original selectors:
    f = filter.copy()
    f['has_set_tag'] = condition['key']
    f['max_id'] = statement['id']
    set_statements = stat.filter_statements(f)

    if len(set_statements) > 0:
        ret.add('((' + ') or ('.join([
            compile_selector_sql(s, stat, prefix, filter)
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
        ret.add(compile_condition_hstore_value(condition, statement, tag_type, stat, prefix, filter))
    elif tag_type[0] == 'column':
        ret.add(compile_condition_column(condition, statement, tag_type, stat, prefix, filter))
    else:
        raise CompileError('unknown tag type {}'.format(tag_type))

    if None in ret:
        ret.remove(None)
    if len(ret) == 0:
        return None

    # merge conditions together, return
    return '(' + ' or '.join(ret) + ')'

def compile_selector_sql(statement, stat, prefix='current.', filter={}, object_type=None):
    filter['object_type'] = object_type

    ret = {
        compile_condition_sql(c, statement, stat, prefix, filter) or 'true'
        for c in statement['selector']['conditions']
    }

    if len(ret) == 0:
        return 'true'

    if 'false' in ret:
        return 'false'

    return ' and '.join(ret)
