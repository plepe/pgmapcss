class config_eval_list(config_base):
    mutable = 3

def eval_list(param):
    return ';'.join(param)

# TESTS
# IN ['foo', 'bar']
# OUT 'foo;bar'
