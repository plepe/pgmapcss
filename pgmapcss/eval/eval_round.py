def eval_round(param):
    if len(param) == 0:
        return ''

    try:
        v = float(param[0])
    except ValueError:
        return ''

    i = 0

    if len(param) > 1:
        i = eval_int(param[1:2])
        i = int(i) if i != '' else 0

    return float_to_str(round(v, i))

# TESTS
# IN ['50.6']
# OUT '51'
# IN ['50.6', '0']
# OUT '51'
# IN ['-50.6', '1']
# OUT '-50.6'
# IN ['-50.6', '-1']
# OUT '-50'
