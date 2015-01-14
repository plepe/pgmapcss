class config_eval_tanh(config_base):
    mutable = 3

def eval_tanh(param, current):
    if len(param) == 0:
        return ''

    try:
        v = float(param[0])
    except ValueError:
        return ''

    v = math.tanh(v)

    return float_to_str(v)

# TESTS
# IN ['0']
# OUT '0'
# IN ['1']
# OUT_ROUND '0.76159'
# IN ['2']
# OUT_ROUND '0.96403'
