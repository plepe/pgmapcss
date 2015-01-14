class config_eval_identical(config_base):
    math_level = 7
    op = ('===', 'eq')
    mutable = 3

    def possible_values(self, param_values, prop, stat):
        if len(param_values) == 0:
            return ( '', 3 )

        if True in param_values:
            return ( { 'true', 'false' }, 3 )
        else:
            return config_base.possible_values(self, param_values, prop, stat)

def eval_identical(param, current):
    # empty parameter list -> all equal
    if len(param) == 0:
        return 'true'

    # identical comparison
    if len(param) != len(set(param)):
        return 'true'

    return 'false';

# TESTS
# IN ['5', '5']
# OUT 'true'
# IN ['5.0', '5', '3.00']
# OUT 'false'
# IN ['3', '5']
# OUT 'false'
# IN []
# OUT 'true'
# IN ['foo', 'bar']
# OUT 'false'
# IN ['foo', '5']
# OUT 'false'
# IN ['foo', 'foo']
# OUT 'true'
