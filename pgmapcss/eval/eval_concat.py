class config_eval_concat(config_base):
    math_level = 6
    op = '.'

def eval_concat(param):
    ret = ''
    for p in param:
        ret += p or ''

    return ret

# TESTS
# IN ['foo', 'bar']
# OUT 'foobar'
