class config_eval_intersection(config_base):
    mutable = 3

def eval_intersection(param):
    if len(param) < 2:
        return ''

    plan = plpy.prepare('select ST_Intersection($1, $2) as geo', ['geometry', 'geometry'])
    res = plpy.execute(plan, param)

    return res[0]['geo']

# TESTS
