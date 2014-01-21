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

    plan = plpy.prepare('select ST_Line_Substring($1, $2, $3) as r', ['geometry', 'float', 'float' ])
    res = plpy.execute(plan, [ param[0], pos0 / length, pos1 / length ])

    return res[0]['r']

# TESTS
# IN ['010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641', '0']
# OUT '010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641'
# IN ['010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641', '10px']
# OUT '010200002031BF0D00020000003FFFE81FFF393A41934741B177B45641295C8F826E393A4152B81E8573B45641'
# IN ['010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641', '10px', '-10px']
# OUT '010200002031BF0D00020000003FFFE81FFF393A41934741B177B45641D6AE5E4186393A41C947813474B45641'
# IN ['010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641', '-20px', '-10px']
# OUT '010200002031BF0D000200000082012E009E393A4140D7E3E374B45641D6AE5E4186393A41C947813474B45641'
# IN ['010200002031BF0D0002000000EC51B8DE163A3A410AD7A36078B45641295C8F826E393A4152B81E8573B45641', '10px', '20px']
# OUT '010200002031BF0D00020000003FFFE81FFF393A41934741B177B4564193AC1961E7393A411CB8DE0177B45641'
