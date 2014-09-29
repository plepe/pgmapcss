import pgmapcss.db as db
from .CompileError import CompileError

def value_format_default(key, value):
    return db.format(value)

def compile_condition_hstore_value(condition, statement, tag_type, stat, prefix, filter):
    ret = ''
    key = tag_type[1]
    column = tag_type[2]

    if condition['op'][0:2] == '! ':
        return None

    # eval() statements
    if condition['op'] == 'eval':
        return None

    # ignore pseudo classes
    if condition['op'] == 'pseudo_class':
        return None

    # eval() statements
    if condition['op'] in ('key_regexp', 'key_regexp_case'):
        return None

    # value-eval() statements
    if condition['value_type'] == 'eval':
        # treat other conditions as has_key
        return prefix + column + ' ? ' + db.format(key);

    # =
    if condition['op'] == '=':
        ret += prefix + column + ' @> ' + db.format({ key: condition['value'] })

    # @=
    elif condition['op'] == '@=' and condition['value_type'] == 'value':
        ret += '(' + ' or '.join([
            prefix + column + ' @> ' + db.format({ key: v })
            for v in condition['value'].split(';')
            ]) + ')'

    else:
        return prefix + column + ' ? ' + db.format(key)

    return ret

def compile_condition_column(condition, statement, tag_type, stat, prefix, filter):
    ret = ''
    key = tag_type[1]

    value_format = value_format_default
    if len(tag_type) > 2:
        value_format = tag_type[2]

    if condition['op'][0:2] == '! ':
        return None

    # eval() statements
    if condition['op'] == 'eval':
        return None

    # ignore pseudo classes
    if condition['op'] == 'pseudo_class':
        return None

    # eval() statements
    if condition['op'] in ('key_regexp', 'key_regexp_case'):
        return None

    # value-eval() statements
    if condition['value_type'] == 'eval':
        # treat other conditions as has_key
        return prefix + db.ident(key) + ' is not null'

    # =
    if condition['op'] == '=':
        ret += prefix + db.ident(key) + ' = ' + value_format(key, condition['value'])

    # @=
    elif condition['op'] == '@=' and condition['value_type'] == 'value':
        ret += prefix + db.ident(key) + ' in (' + ', '.join([
                value_format(key, v)
                for v in condition['value'].split(';')
            ]) + ')'

    else:
        return prefix + db.ident(key) + ' is not null'

    return ret

def compile_condition_sql(condition, statement, stat, prefix='current.', filter={}):
    # ignore generated tags (identified by leading .)
    if condition['key'][0] == '.':
        f = filter.copy()
        f['has_set_tag'] = condition['key']
        f['max_id'] = statement['id']
        set_statements = stat.filter_statements(f)

        if len(set_statements) == 0:
            return 'false'

        return '((' + ') or ('.join([
            compile_selector_sql(s, stat, prefix, filter)
            for s in set_statements
        ]) + '))'

    tag_type = stat['database'].tag_type(condition['key'])

    if tag_type is None:
        return None
    elif tag_type[0] == 'hstore-value':
        return compile_condition_hstore_value(condition, statement, tag_type, stat, prefix, filter)
    elif tag_type[0] == 'column':
        return compile_condition_column(condition, statement, tag_type, stat, prefix, filter)
    else:
        raise CompileError('unknown tag type {}'.format(tag_type))

def compile_selector_sql(statement, stat, prefix='current.', filter={}):
    ret = {
        compile_condition_sql(c, statement, stat, prefix, filter) or 'true'
        for c in statement['selector']['conditions']
    }

    if len(ret) == 0:
        return 'true'

    if 'false' in ret:
        return 'false'

    return ' and '.join(ret)
