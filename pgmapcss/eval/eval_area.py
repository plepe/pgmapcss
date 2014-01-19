def eval_area(param):
    if len(param) == 0:
        return ''

    plan = plpy.prepare('select ST_Area($1) as area', ['geometry'])
    res = plpy.execute(plan, param)

    zoom = eval_metric(['1u'])

    return res[0]['area'] * zoom ** 2
