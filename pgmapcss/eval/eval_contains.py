class config_eval_contains(config_base):
    math_level = 7
    op = '~='
    mutable = 3

    def possible_values(self, param_values, prop, stat):
        if len(param_values) < 2:
            return ( '', 3 )

        if True in param_values:
            return ( { 'true', 'false' }, 3 )
        else:
            return config_base.possible_values(self, param_values, prop, stat)

def eval_contains(param):
    if len(param) < 2:
        return ''

    l = param[0].split(';')

    return 'true' if param[1] in l else 'false'

# TESTS
# IN ['restaurant;bar', 'bar']
# OUT 'true'
# IN ['restaurant;bar', 'pub']
# OUT 'false'
# IN ['restaurant;bar', 'rest']
# OUT 'false'
