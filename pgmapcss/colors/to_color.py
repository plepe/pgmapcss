def to_color(value):
    import re
    if re.match('#[a-fA-F0-9]{6,8}', value):
        return value

    return None

def check_color(value):
    ret = to_color(value)

    if ret is None:
        warning("Warning: Unknown color '{}'".format(value))

    return ret
