class config_eval_floor(config_base):
    mutable = 3

def eval_floor(param):
    import math
    if len(param) == 0:
        return ''

    try:
        v = float(param[0])
    except ValueError:
        return ''

    v = math.floor(v)

    return float_to_str(v)

# TESTS
# IN ['50.6']
# OUT '50'
# IN ['-50.6']
# OUT '-51'
