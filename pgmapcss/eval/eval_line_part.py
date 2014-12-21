class config_eval_line_part(config_base):
    mutable = 2

def eval_line_part(param):
    if len(param) == 0:
        return ''

    if len(param) == 1:
        return param[0]

    length = float(eval_line_length([param[0]]))

    # start position
    pos0 = eval_metric([ param[1], 'px' ])
    if pos0 == '':
        pos0 = 0.0
    else:
        pos0 = float(pos0)

    if pos0 < 0.0:
        pos0 = length + pos0

    if pos0 < 0.0:
        pos0 = 0.0

    if pos0 > length:
        pos0 = length

    # end position
    if len(param) >= 3:
        pos1 = eval_metric([ param[2], 'px' ])
        if pos1 == '':
            pos1 = length
        else:
            pos1 = float(pos1)

    else:
        pos1 = length

    if pos1 < 0.0:
        pos1 = length + pos1

    if pos1 < 0.0:
        pos1 = 0.0

    if pos1 < pos0:
        return ''

    if pos1 > length:
        pos1 = length

    try:
        plan = plpy.prepare('select ST_Transform(ST_Line_Substring(ST_Transform($1, {unit.srs}), $2, $3), {db.srs}) as r', ['geometry', 'float', 'float' ])
        res = plpy.execute(plan, [ param[0], pos0 / length, pos1 / length ])
    except Exception as err:
        plpy.warning('{} | Eval::line_part({}): Exception: {}'.format(current['object']['id'], param, err))
        return ''

    return res[0]['r']

# TESTS
# IN ['010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641', '0']
# OUT '010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641'
# IN ['010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641', '10px']
# OUT '010200002031BF0D0002000000582CE91FFF393A41E04841B177B45641295C8F826E393A4152B81E8573B45641'
# IN ['010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641', '10px', '-10px']
# OUT '010200002031BF0D0002000000582CE91FFF393A41E04841B177B45641BD815E4186393A417C46813474B45641'
# IN ['010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641', '-20px', '-10px']
# OUT '010200002031BF0D000200000051A72D009E393A41A6D4E3E374B45641BD815E4186393A417C46813474B45641'
# IN ['010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641', '10px', '20px']
# OUT '010200002031BF0D0002000000582CE91FFF393A41E04841B177B45641C4061A61E7393A41B6BADE0177B45641'
