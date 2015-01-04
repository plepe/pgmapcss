class config_eval_line_interpolate_line(config_base):
    mutable = 2

def eval_line_interpolate_point(param):
    if len(param) == 0 or not param[0]:
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

    try:
        plan = plpy.prepare('select ST_Line_Interpolate_Point($1, $2) as r', ['geometry', 'float'])
        res = plpy.execute(plan, [ param[0], float(f) ])
    except Exception as err:
        debug('Eval::line_interpolate_point({}): Exception: {}'.format(param, err))
        return ''

    return res[0]['r']

# TESTS
# IN ['010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641']
# OUT '010100002031BF0D000AD7A3B0C2393A41AE47E1F275B45641'
# IN ['010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641', '0u']
# OUT '010100002031BF0D00EC51B8DE163A3A410AD7A36078B45641'
# IN ['010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641', '5px']
# OUT '010100002031BF0D0022BF50FF0A3A3A41F58FF20878B45641'
# IN ['', '5px']
# OUT ''

# IN [ '010200002031BF0D0003000000C3F5281C3C3C3A410AD7A3C0B1B55641666666A6B13B3A41EC51B8FEB9B556415C8FC235823B3A4185EB51B8BCB55641', '52.61864905625409' ]
# OUT '010100002031BF0D00D17EBEC1C13B3A41760E4209B9B55641'
# IN [ '010200002031BF0D000300000085EB51789E3B3A4148E17A749AB556413D0AD763E83B3A4133333373A1B55641000000C0233C3A41C3F5280CA7B55641', '7.314706354219713' ]
# OUT '010100002031BF0D00860A74D2AE3B3A4172699C009CB55641'
