class config_eval_ceil(config_base):
    mutable = 3

def eval_ceil(param):
    import math
    if len(param) == 0:
        return ''

    try:
        v = float(param[0])
    except ValueError:
        return ''

    v = math.ceil(v)

    return float_to_str(v)

# TESTS
# IN ['50.6']
# OUT '51'
# IN ['-50.6']
# OUT '-50'
