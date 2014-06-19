import pgmapcss.db as db
from .stat import stat_filter_statements

def compile_condition_sql(condition, statement, stat, prefix='current.', filter={}):
    ret = ''
    final_value = None

    if 'value' in condition:
        final_value = db.format(condition['value'])

    # ignore generated tags (identified by leading .)
    if condition['key'][0] == '.':
        f = filter.copy()
        f['has_set_tag'] = condition['key']
        f['max_id'] = statement['id']
        set_statements = stat_filter_statements(stat, f)

        if len(set_statements) == 0:
            return 'false'

        return '((' + ') or ('.join([
            compile_selector_sql(s, stat, prefix, filter)
            for s in set_statements
        ]) + '))'

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

def compile_selector_sql(statement, stat, prefix='current.', filter={}):
    ret = [
        compile_condition_sql(c, statement, stat, prefix, filter) or 'true'
        for c in statement['selector']['conditions']
    ]

    if len(ret) == 0:
        return 'true'

    return ' and '.join(ret)
