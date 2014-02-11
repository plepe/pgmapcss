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
