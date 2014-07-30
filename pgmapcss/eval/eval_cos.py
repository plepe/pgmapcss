class config_eval_cos(config_base):
    mutable = 3

def eval_cos(param):
    if len(param) == 0:
        return ''

    try:
        v = float(param[0])
    except ValueError:
        return ''

    v = math.cos(TO_RADIANS(v))

    return float_to_str(v)

# TESTS
# IN ['0']
# OUT '1'
# IN ['90']
# OUT_ROUND '0'
# IN ['45']
# OUT_ROUND '0.70711'
