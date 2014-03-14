class config_eval_le(config_base):
    math_level = 7
    op = '<='
    mutable = 3

def eval_le(param):
    if len(param) < 2:
        return ''

    a = eval_metric(param[0:1])
    a = float(a) if a != '' else 0.0

    for p in param[1:]:
        b = eval_metric([p])
        b = float(b) if b != '' else 0.0

        if not a <= b:
            return 'false'

        a = b

    return 'true'

# TESTS
# IN ['1', '2', '2.0', '3']
# OUT 'true'
# IN ['1', '2', '3']
# OUT 'true'
# IN ['3', '2', '1']
# OUT 'false'
# IN ['3', '2', '2.0', '1']
# OUT 'false'
# IN ['1', '2']
# OUT 'true'
# IN ['2', '1']
# OUT 'false'
# IN ['1.0', '1']
# OUT 'true'
