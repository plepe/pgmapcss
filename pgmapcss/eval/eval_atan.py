class config_eval_atan(config_base):
    mutable = 3

def eval_atan(param, current):
    if len(param) == 0:
        return ''

    try:
        v = float(param[0])
    except ValueError:
        return ''

    v = FROM_RADIANS(math.atan(v))

    return float_to_str(v)

# TESTS
# IN ['0']
# OUT '0'
# IN ['1']
# OUT_ROUND '45'
