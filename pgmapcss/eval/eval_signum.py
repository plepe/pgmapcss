class config_eval_signum(config_base):
    mutable = 3

def eval_signum(param, current):
    if len(param) == 0:
        return ''

    try:
        v = float(param[0])
    except ValueError:
        return ''

    if v < 0.0:
        return '-1'
    if v > 0.0:
        return '1'
    return '0'

# TESTS
# IN ['1']
# OUT '1'
# IN ['-5']
# OUT '-1'
# IN ['0']
# OUT '0'
