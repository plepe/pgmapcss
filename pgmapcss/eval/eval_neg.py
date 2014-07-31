class config_eval_neg(config_base):
    math_level = 10
    op = '-'
    unary = True
    mutable = 3

def eval_neg(param):
    if len(param) == 0:
        return ''

    v = eval_metric([param[0]])

    if v == '':
        return ''

    return float_to_str(-1.0 * float(v))

# TESTS
# IN ['5']
# OUT '-5'
# IN ['5.5']
# OUT '-5.5'
# IN ['false']
# OUT ''
# IN ['-5']
# OUT '5'
