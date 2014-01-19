def eval_int(param):
    if len(param) == 0:
        return ''

    try:
        v = float(param[0])
        return '%d' % v
    except ValueError:
        return ''

# TESTS
# IN ['5']
# OUT '5'
# IN ['5.0']
# OUT '5'
# IN ['5.9']
# OUT '5'
# IN ['-5.9']
# OUT '-5'
