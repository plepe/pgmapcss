class config_eval_num(config_base):
    mutable = 3

def eval_num(param):
    if len(param) == 0:
        return ''

    try:
        value = float(param[0])
    except ValueError:
        return ''

    return float_to_str(value)

# TESTS
# IN ['5.0']
# OUT '5'
# IN ['-5']
# OUT '-5'
# IN ['-5.5']
# OUT '-5.5'
# IN ['foobar']
# OUT ''
# IN ['']
# OUT ''
