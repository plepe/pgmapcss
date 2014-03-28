class config_eval_switch(config_base):
    mutable = 3

    def possible_values(self, param_values, prop, stat):
        if param_values[0] is not True:
            return config_base.possible_values(self, param_values, prop, stat)

        ret = {}

        for i in range(1, len(param) - 1, 2):
            ret.add(param[i + 1])

        if len(param) % 2 == 0:
            ret.add(param[-1])

        return ( ret, 3 )

def eval_switch(param):
    if len(param) == 0:
        return ''

    value = param[0]

    for i in range(1, len(param) - 1, 2):
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
# IN ['4', '1', 'foo', '4', 'bar', 'else']
# OUT 'bar'
# IN ['else', '1', 'foo', '5', '4', 'else']
# OUT 'else'
# IN ['4', 'else']
# OUT 'else'
