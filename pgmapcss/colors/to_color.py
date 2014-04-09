def to_color(value):
    import re

    if value is None:
        return None

    if re.match('#[a-fA-F0-9]{6,8}', value):
        return value

    if re.match('#[a-fA-F0-9]{3,4}', value):
        r = '#'
        for i in range(1, len(value)):
            r += value[i] + value[i]

        return r

    try:
        from .color_names import color_names
    except ValueError:
        global color_names

    if value in color_names:
        return color_names[value]

    return None

def check_color(value):
    if value is None or value == '':
        return None

    ret = to_color(value)

    if ret is None:
        debug("Warning: Unknown color '{}'".format(value))

    return ret
