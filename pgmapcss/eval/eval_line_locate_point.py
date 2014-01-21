def eval_line_locate_point(param):
    if len(param) < 2:
        return ''

    plan = plpy.prepare('select ST_Line_Locate_Point($1, $2) * ST_Length($1) as r', ['geometry', 'geometry'])
    res = plpy.execute(plan, [ param[0], param[1] ])

    return eval_metric([ repr(res[0]['r']) + 'u' ])

# IN ['010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641', '010100002031BF0D00EC51B8DE163A3A410AD7A36078B45641']
# OUT '0'
# IN ['010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641', '010100002031BF0D0096A850FF0A3A3A414E8FF20878B45641']
# OUT '5'
