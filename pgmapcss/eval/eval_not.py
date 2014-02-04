def eval_not(param):
    if len(param) == 0:
        return ''

    if eval_boolean(param[0:1]) == 'true':
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
