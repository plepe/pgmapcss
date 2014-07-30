class config_eval_acos(config_base):
    mutable = 3

def eval_acos(param):
    if len(param) == 0:
        return ''

    try:
        v = float(param[0])
    except ValueError:
        return ''

    v = FROM_RADIANS(math.acos(v))

    return float_to_str(v)

# TESTS
# IN ['0']
# OUT '90'
# IN ['0.5']
# OUT_ROUND '60'
# IN ['1']
# OUT_ROUND '0'
