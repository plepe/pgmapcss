class config_eval_exp(config_base):
    mutable = 3

def eval_exp(param, current):
    if len(param) == 0:
        return ''

    try:
        v = float(param[0])
    except ValueError:
        return ''

    return float_to_str(math.exp(v))

# TESTS
# IN ['1']
# OUT_ROUND '2.71828'
# IN ['-5']
# OUT_ROUND '0.00674'
# IN ['0']
# OUT '1'
