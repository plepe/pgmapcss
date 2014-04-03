import pgmapcss.db as db

def compile_condition_sql(condition, statement, stat, prefix='current.'):
    ret = ''
    final_value = None

    if 'value' in condition:
        final_value = db.format(condition['value'])

    # ignore generated tags (identified by leading .)
    if condition['key'][0] == '.':
        return None

    if condition['op'][0:2] == '! ':
        return None

    # eval() statements
    if condition['op'] == 'eval':
        return None

    # value-eval() statements
    if condition['value_type'] == 'eval':
        # treat other conditions as has_key
        return prefix + 'tags ? ' + db.format(condition['key']);

    # =
    if condition['op'] == '=':
        ret += prefix + 'tags @> ' + db.format({ condition['key']: condition['value'] })

    else:
        return prefix + 'tags ? ' + db.format(condition['key']);

    return ret;

def compile_selector_sql(statement, stat, prefix='current.'):
    ret = [
        compile_condition_sql(c, statement, stat, prefix=prefix) or 'true'
        for c in statement['selector']['conditions']
    ]

    return ' and '.join(ret)
