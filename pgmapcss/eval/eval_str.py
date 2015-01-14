class config_eval_str(config_base):
    mutable = 3

def eval_str(param, current):
    if len(param) == 0:
        return ''

    return param[0]

# TESTS
# IN ['foo']
# OUT 'foo'
