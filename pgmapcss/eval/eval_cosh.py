class config_eval_cosh(config_base):
    mutable = 3

def eval_cosh(param):
    if len(param) == 0:
        return ''

    try:
        v = float(param[0])
    except ValueError:
        return ''

    v = math.cosh(v)

    return float_to_str(v)

# TESTS
# IN ['0']
# OUT '1'
# IN ['1']
# OUT_ROUND '1.54308'
# IN ['2']
# OUT_ROUND '3.76220'
