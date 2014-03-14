class config_eval_sqrt(config_base):
    mutable = 3

def eval_sqrt(param):
    import math
    if len(param) == 0:
        return ''

    f = eval_metric([param[0]])
    if f == '':
        return ''

    f = float(f)

    if f < 0:
        return ''

    f = math.sqrt(f)

    return float_to_str(f)

# TESTS
# IN ['4']
# OUT '2'
# IN ['2']
# OUT '1.4142135623730951'
# IN ['1']
# OUT '1'
# IN ['-2']
# OUT ''
# IN ['0']
# OUT '0'
