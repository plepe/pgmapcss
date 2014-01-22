def eval_line_interpolate_point(param):
    if len(param) == 0:
        return ''

    if len(param) == 1:
        f = 0.5
        l = None

    else:
        l = eval_line_length([param[0]])
        f = eval_metric([param[1], 'px'])
        if f == '':
            return ''
        f = float(f) / float(l)

    if f < 0.0:
        f = 0.0
    elif f > 1.0:
        f = 1.0

    plan = plpy.prepare('select ST_Line_Interpolate_Point($1, $2) as r', ['geometry', 'float'])
    res = plpy.execute(plan, [ param[0], float(f) ])

    return res[0]['r']

# TESTS
# IN ['010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641']
# OUT '010100002031BF0D000AD7A3B0C2393A41AE47E1F275B45641'
# IN ['010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641', '0u']
# OUT '010100002031BF0D00EC51B8DE163A3A410AD7A36078B45641'
# IN ['010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641', '5px']
# OUT '010100002031BF0D0022BF50FF0A3A3A41F58FF20878B45641'
