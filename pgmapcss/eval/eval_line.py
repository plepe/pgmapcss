def eval_line(param):
    if len(param) == 0:
        return ''

    if len(param) == 1:
        param = param[0].split(';')

    if len(param) == 1:
        param = param[0]
        plan = plpy.prepare('select ST_MakeLine($1) as r', ['geometry'])

    else:
        plan = plpy.prepare('select ST_MakeLine($1) as r', ['geometry[]'])

    res = plpy.execute(plan, param)

    return res[0][r]
