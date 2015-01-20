def to_float(v, default=None):
    try:
        return float(v)
    except ValueError:
        return default
    except TypeError:
        return default
def to_int(v, default=None):
    try:
        return int(v)
    except ValueError:
        return default
    except TypeError:
        return default
def float_to_str(v, default=None):
    r = repr(v)
    if r[-2:] == '.0':
        r = r[:-2]
    return r
def debug(text, current=None):
    try:
        prefix = current['object']['id'] + ' | '
    except:
        prefix = ''

    plpy.warning(prefix + text)

class config_base:
    math_level = None
    op = None
    unary = False
    aliases = None
    eval_options = dict()
# eval options contains additional information, e.g. requirements
# if the possible_values or possible_values_all functions are overridden, these
# function need to return eval_options as third value
    mutable = 0
# 'mutable' says whether a function returns different output for the same set
# of input parameters:
# 0 .. volatile, may return different value on each call (e.g. random())
# 1 .. always returns the same value for the current object (e.g. osm_id())
# 2 .. always returns the same value for the current view (e.g. zoom())
# 3 .. static, always returns the same value (e.g. 2+3 = 5)

    def __init__(self, func):
        import re

        if not re.match('[a-zA-Z_0-9]+$', func):
            raise Exception('Illegal eval function name: ' + func)

        self.func = func

    def compiler(self, param, eval_param, stat):
        return 'eval_' + self.func + '([' + ', '.join(param) + ']' + eval_param + ')'

    def __call__(self, param, stat):
        try:
            current
        except NameError:
            import pgmapcss.eval
            return pgmapcss.eval.eval_functions.call(self.func, param, stat)
        else:
            return eval(self.compiler(param, '', {}))

# list of possible values the function returns for the set of input parameters. # possible types of returns a tuple with the first element being one of:
#   str .. the function always returns the given value (e.g. 2+3 = 5)
#   None .. the function always returns None
#   set .. the function may return the following values
#          (e.g. zoom() => { 1, 2, 3, ..., 18 }
#   True .. it's not possible to predict the result of this function (e.g. random())
# the second element is the mutability, see above
# an optional third element (dict) contains additional information, e.g. requirements:
# {
#   'requirements': { 'geo', 'meta' }
# }
    def possible_values(self, param_values, prop, stat):
        m = self.mutable

        if True in param_values:
            return ( True, 0, self.eval_options )

        if callable(m):
            m = self.mutable(param_values, stat)

        if m == 3:
            return ( self(param_values, stat), m, self.eval_options )

        return ( True, m, self.eval_options )
