class config_eval_nonidentical(config_base):
    math_level = 7
    op = ('!==', 'ne')
    mutable = 3

    def possible_values(self, param_values, prop, stat):
        if len(param_values) == 0:
            return ( 'false', 3 )

        if True in param_values:
            return ( { 'true', 'false' }, 3 )
        else:
            return config_base.possible_values(self, param_values, prop, stat)

def eval_nonidentical(param):
    # empty parameter list -> all equal
    if len(param) == 0:
        return 'false'

    # identical comparison
    if len(param) != len(set(param)):
        return 'false'

    return 'true';

# TESTS
# IN ['5', '5']
# OUT 'false'
# IN ['5', '5', '3.00']
# OUT 'false'
# IN ['5.0', '5', '3.00']
# OUT 'true'
# IN ['3', '5']
# OUT 'true'
# IN []
# OUT 'false'
# IN ['foo', 'bar']
# OUT 'true'
# IN ['foo', '5']
# OUT 'true'
# IN ['foo', 'foo']
# OUT 'false'
