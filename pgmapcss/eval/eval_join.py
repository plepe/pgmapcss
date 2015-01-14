class config_eval_join(config_base):
    mutable = 3

def eval_join(param, current):
    if len(param) < 2:
        return ''

    if len(param) > 2:
        l = param[1:]
    else:
        l = param[1].split(';')

    return param[0].join(l)

# TESTS
# IN [', ', 'restaurant;bar']
# OUT 'restaurant, bar'
# IN [', ', 'restaurant', 'bar']
# OUT 'restaurant, bar'
