# Note: JOSM accepted "named" colors, e.g. "building#004400" -> ignore string before color hash
def to_color(value):
    import re

    if value is None:
        return None

    m = re.match('[\w_]*(#[a-fA-F0-9]{6,8})', value)
    if m:
        return m.group(1)

    m = re.match('[\w_]*(#[a-fA-F0-9]{3,4})', value)
    if m:
        value = m.group(1)
        r = '#'
        for i in range(1, len(value)):
            r += value[i] + value[i]

        return r

    try:
        from .color_names import color_names
    except SystemError:
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
