class config_eval_line_locate_azimuth(config_base):
    mutable = 2

def eval_line_locate_azimuth(param):
    if len(param) < 2:
        return ''

    l = float(eval_line_length([param[0]]))

    f = eval_metric([param[1], 'px'])
    if f == '':
        # seems to be a geometry
        f = float(eval_line_locate_point([ param[0], param[1] ]))
    else:
        f = float(f)

    if f < 0.0:
        f = 0.0
    elif f > l:
        f = l

    dist = 1.0
    if len(param) > 2:
        dist = eval_metric([param[2], 'px'])
        if dist == '':
            dist = 1.0
        else:
            dist = float(dist)

    f1 = f - dist
    if f1 < 0.0:
        f1 = 0.0

    f2 = f + dist
    if f2 > l:
        f2 = l

    plan = plpy.prepare('select degrees(ST_Azimuth(ST_Line_Interpolate_Point($1, $2), ST_Line_Interpolate_Point($1, $3))) as r1, degrees(ST_Azimuth(ST_Line_Interpolate_Point($1, $3), ST_Line_Interpolate_Point($1, $4))) as r2', ['geometry', 'float', 'float', 'float'])
    res = plpy.execute(plan, [ param[0], f1 / l, f / l, f2 / l ])

    r1 = res[0]['r1']
    r2 = res[0]['r2']

    if f1 != 0.0 and f2 != l:
        if r1 < 90 and r2 > 270:
            r2 -= 360
        if r2 < 90 and r1 > 270:
            r1 -= 360

        r = r1 + (r2 - r1) / 2.0

        if r < 0:
            r += 360

    elif f1 == 0.0:
        r = r2

    elif f2 == l:
        r = r1

    else:
        return ''

    #plpy.notice(l, f, f1, f2, res[0], r)
    return str(FROM_DEGREES(r))

# TESTS
# IN ['010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641', '010100002031BF0D0096A850FF0A3A3A414E8FF20878B45641']
# OUT '263.416763627542'
# IN ['010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641', '5.000000565986081']
# OUT '263.416763627542'
# IN ['010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641', '0']
# OUT '263.4167636386304'
# IN ['010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641', '100']
# OUT '263.4167636386304'
