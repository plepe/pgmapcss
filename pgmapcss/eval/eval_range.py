class config_eval_range(config_base):
    mutable = 3

def eval_range(param):
    if len(param) < 2:
        return ''

    step = 1.0
    if len(param) > 2:
        try:
            step = float(param[2])
        except ValueError:
            return ''

    try:
        start = float(param[0])
    except ValueError:
        return ''

    try:
        stop = float(param[1])
    except ValueError:
        return ''

    l = []

    if step > 0:
        while start <= stop:
            l.append(float_to_str(start))
            start += step

    elif step < 0:
        while start >= stop:
            l.append(float_to_str(start))
            start += step

    else:
        return ''

    return ';'.join(l)

# TESTS
# IN ['1', '3']
# OUT '1;2;3'
# IN ['1', '5', '2']
# OUT '1;3;5'
# IN ['1', '4', '2']
# OUT '1;3'
# IN ['5', '-5', '-2.5']
# OUT '5;2.5;0;-2.5;-5'
# IN ['-5', '5', '-2.5']
# OUT ''
