def eval_centroid(param):
    if not len(param):
        return ''

    plan = plpy.prepare('select ST_Centroid($1) as r', ['geometry'])
    res = plpy.execute(plan, param)

    return res[0]['r']
