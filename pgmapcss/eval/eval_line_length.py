def eval_line_length(param):
    if len(param) == 0:
        return ''

    plan = plpy.prepare('select ST_Length($1) as r', ['geometry'])
    res = plpy.execute(plan, param[0])
    l = res[0]['r']

    return eval_metric([ l + 'u' ])
