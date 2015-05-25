class config_eval_sum(config_base):
    mutable = 3

def eval_sum(param):
    if len(param) == 0:
        return ''
    if len(param) == 1:
        param = param[0].split(';')

    values = []
    for v in param:
        try:
            v = float(v)
        except ValueError:
            v = ''
        values.append(v)

    values = [ float(v) for v in values if v != '' ]

    if len(values) == 0:
        return ''

    return float_to_str(sum(values))

# TESTS
# IN ['1.0', '5', '3']
# OUT '9'
# IN ['1.0', '']
# OUT '1'
# IN ['1;4;5']
# OUT '10'
# IN []
# OUT ''
# IN ['1;;5']
# OUT '6'
# IN ['']
# OUT ''
