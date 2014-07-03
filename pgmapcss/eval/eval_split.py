class config_eval_split(config_base):
    mutable = 3

def eval_split(param):
    if len(param) < 2:
        return ''

    l = param[1].split(param[0])

    return ';'.join(l)

# TESTS
# IN ['--', 'foo--bar']
# OUT 'foo;bar'
