class config_eval_collect(config_base):
    mutable = 3

def eval_collect(param, current):
    if len(param) < 2:
        return ''

    # if one of the parameters is None, the other parameter is the collect
    if param[0] in (None, ''):
        return param[1]
    if param[1] in (None, ''):
        return param[0]

    try:
        plan = plpy.prepare('select ST_CollectionHomogenize(ST_Collect($1, $2)) as geo', ['geometry', 'geometry'])
        res = plpy.execute(plan, param)
    except Exception as err:
        debug('Eval::collect({}): Exception: {}'.format(param, err))
        return ''

    return res[0]['geo']

# TESTS
