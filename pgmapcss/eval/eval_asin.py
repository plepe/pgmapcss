class config_eval_asin(config_base):
    mutable = 3

def eval_asin(param):
    if len(param) == 0:
        return ''

    try:
        v = float(param[0])
    except ValueError:
        return ''

    v = FROM_RADIANS(math.asin(v))

    return float_to_str(v)

# TESTS
# IN ['0']
# OUT '0'
# IN ['0.5']
# OUT_ROUND '30'
# IN ['1']
# OUT_ROUND '90'
