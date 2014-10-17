class config_eval_centroid(config_base):
    mutable = 3

def eval_centroid(param, current):
    if not len(param):
        return ''

    plan = plpy.prepare('select ST_Centroid($1) as r', ['geometry'])
    res = plpy.execute(plan, param)

    return res[0]['r']

# TESTS
# IN ['010300002031BF0D000100000004000000AE47E1BA1F52354185EB51B83EAE5641C3F528DC1F5235413D0AD7D33FAE5641295C8F4224523541000000B03EAE5641AE47E1BA1F52354185EB51B83EAE5641']
# OUT '010100002031BF0D00888888482152354140A70D143FAE5641'
