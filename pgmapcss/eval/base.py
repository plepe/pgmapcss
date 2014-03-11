def to_float(v, default=None):
    try:
        return float(v)
    except ValueError:
        return default
def to_int(v, default=None):
    try:
        return int(v)
    except ValueError:
        return default
def float_to_str(v, default=None):
    r = repr(v)
    if r[-2:] == '.0':
        r = r[:-2]
    return r
def debug(text):
    plpy.notice(text)

class config_base:
    math_level = None
    op = None
    unary = False

    def __init__(self, func):
        self.func = func
