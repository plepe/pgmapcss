class config_eval_tan(config_base):
    mutable = 3

def eval_tan(param):
    if len(param) == 0:
        return ''

    try:
        v = float(param[0])
    except ValueError:
        return ''

    v = math.tan(TO_RADIANS(v))

    return float_to_str(v)

# TESTS
# IN ['0']
# OUT '0'
# IN ['45']
# OUT_ROUND '1'
