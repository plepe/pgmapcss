class config_eval_not(config_base):
    math_level = 10
    op = '!'
    unary = True
    mutable = 3

    def possible_values(self, param_values, prop, stat):
        if len(param_values) == 0:
            return ( '', 3 )

        if param_values[0] == True:
            return ( { 'true', 'false' }, 3 )
        else:
            return config_base.possible_values(self, param_values, prop, stat)

def eval_not(param, current):
    if len(param) == 0:
        return ''

    if eval_boolean(param[0:1], current) == 'true':
        return 'false'

    return 'true'

# TESTS
# IN ['foo']
# OUT 'false'
# IN ['true']
# OUT 'false'
# IN ['false']
# OUT 'true'
# IN ['0']
# OUT 'true'
