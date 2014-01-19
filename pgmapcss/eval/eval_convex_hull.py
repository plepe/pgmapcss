def eval_convex_hull(param):
    if len(param) == 0:
        return ''

    plan = plpy.prepare('select ST_ConvexHull($1) as r', ['geometry'])
    res = plpy.execute(plan, param)

    return res[0]['r']
