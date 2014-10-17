class config_eval_int(config_base):
    mutable = 3

def eval_int(param, current):
    if len(param) == 0:
        return ''

    try:
        v = float(param[0])
        return '%d' % v
    except ValueError:
        return ''

# TESTS
# IN ['5']
# OUT '5'
# IN ['5.0']
# OUT '5'
# IN ['5.9']
# OUT '5'
# IN ['-5.9']
# OUT '-5'
