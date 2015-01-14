class config_eval_reverse(config_base):
    mutable = 3

def eval_reverse(param, current):
    if len(param) == 0:
        return ''

    l = param[0].split(';')

    l.reverse()

    return ';'.join(l)

# TESTS
# IN ['foo;bar']
# OUT 'bar;foo'
