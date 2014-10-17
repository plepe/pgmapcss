class config_eval_sinh(config_base):
    mutable = 3

def eval_sinh(param, current):
    if len(param) == 0:
        return ''

    try:
        v = float(param[0])
    except ValueError:
        return ''

    v = math.sinh(v)

    return float_to_str(v)

# TESTS
# IN ['0']
# OUT '0'
# IN ['1']
# OUT_ROUND '1.17520'
# IN ['2']
# OUT_ROUND '3.62686'
