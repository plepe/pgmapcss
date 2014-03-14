class config_eval_max(config_base):
    mutable = 3

def eval_max(param):
    if len(param) == 0:
        return ''
    if len(param) == 1:
        param = param[0].split(';')

    values = [ eval_metric([v]) for v in param ]
    values = [ float(v) for v in values if v != '' ]

    while '' in values:
        values.remove('')
    if len(values) == 0:
        return ''

    return float_to_str(max(values))

# TESTS
# IN ['1.0', '5', '3']
# OUT '5'
# IN ['1.0', '']
# OUT '1'
# IN ['1;4;5']
# OUT '5'
# IN ['1px;1000u']
# OUT '418.35829844643484'
# IN []
# OUT ''
# IN ['1;;5']
# OUT '5'
# IN ['']
# OUT ''
