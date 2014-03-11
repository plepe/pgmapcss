class config_eval_equal(config_base):
    math_level = 7
    op = '=='

def eval_equal(param):
    # empty parameter list -> all equal
    if len(param) == 0:
        return 'true'

    # identical comparison
    if len(set(param)) == 1:
        return 'true'

    # convert all values to numbers
    values = [ eval_metric([v]) for v in param ]

    if not '' in values and len(set(values)) == 1:
        return 'true'

    return 'false';

# TESTS
# IN ['5.0', '5']
# OUT 'true'
# IN ['5.0', '5', '3.00']
# OUT 'false'
# IN ['5', '5']
# OUT 'true'
# IN []
# OUT 'true'
# IN ['foo', 'bar']
# OUT 'false'
# IN ['foo', '5.0']
# OUT 'false'
# IN ['foo', 'foo']
# OUT 'true'
