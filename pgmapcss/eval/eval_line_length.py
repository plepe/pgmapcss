class config_eval_line_length(config_base):
    mutable = 2

def eval_line_length(param):
    if len(param) == 0:
        return ''

    if not param[0]:
        return ''

    plan = plpy.prepare('select ST_Length(ST_Transform($1, {unit.srs})) as r', ['geometry'])
    res = plpy.execute(plan, [param[0]])
    l = res[0]['r']

    return eval_metric([ repr(l) + 'u' ])

# TESTS
# IN ['010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641']
# OUT '70.90230802606656'
# IN ['']
# OUT ''
