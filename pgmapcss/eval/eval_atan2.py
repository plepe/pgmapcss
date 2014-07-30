class config_eval_atan2(config_base):
    mutable = 3

def eval_atan2(param):
    if len(param) < 2:
        return ''

    try:
        v1 = float(param[0])
    except ValueError:
        return ''

    try:
        v2 = float(param[1])
    except ValueError:
        return ''

    v = FROM_RADIANS(math.atan2(v1, v2))

    return float_to_str(v)

# TESTS
# IN ['0', '0']
# OUT '0'
# IN ['1', '5']
# OUT_ROUND '11.30993'
