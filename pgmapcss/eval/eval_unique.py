class config_eval_unique(config_base):
    mutable = 3

def eval_unique(param):
    if len(param) == 0:
        return ''

    if len(param) == 1:
        param = param[0].split(';')

    return ';'.join(set(param))

# TESTS
# IN ['foo;bar;foo']
# OUT_SET 'foo;bar'
