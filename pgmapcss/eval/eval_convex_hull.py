class config_eval_convex_hull(config_base):
    mutable = 3

def eval_convex_hull(param):
    if len(param) == 0:
        return ''

    try:
        plan = plpy.prepare('select ST_ConvexHull($1) as r', ['geometry'])
        res = plpy.execute(plan, param)
    except Exception as err:
        debug('Eval::convex_hull({}): Exception: {}'.format(param, err))
        return ''

    return res[0]['r']

# TEST
# IN ['010300002031BF0D000100000004000000AE47E1BA1F52354185EB51B83EAE5641C3F528DC1F5235413D0AD7D33FAE5641295C8F4224523541000000B03EAE5641AE47E1BA1F52354185EB51B83EAE5641']
# OUT '010300002031BF0D000100000004000000295C8F4224523541000000B03EAE5641AE47E1BA1F52354185EB51B83EAE5641C3F528DC1F5235413D0AD7D33FAE5641295C8F4224523541000000B03EAE5641'
