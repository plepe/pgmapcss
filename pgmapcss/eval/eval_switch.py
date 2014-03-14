class config_eval_switch(config_base):
    mutable = 3

def eval_switch(param):
    if len(param) == 0:
        return ''

    value = param[0]

    for i in range(1, len(param), 2):
        comp_values = param[i].split(';')

        if value in comp_values:
            return param[i + 1]

    if len(param) % 2 == 0:
        return param[-1]

    return ''

# TESTS
# IN ['5', '1', 'foo', '5', 'bar']
# OUT 'bar'
# IN ['4', '1', 'foo', '5', 'bar']
# OUT ''
# IN ['4', '1', 'foo', '4;5', 'bar']
# OUT 'bar'
# IN ['4', '1', 'foo', '5', 'bar', 'else']
# OUT 'else'
# IN ['4', 'else']
# OUT 'else'
