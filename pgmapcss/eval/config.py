from .functions import Functions
from pkg_resources import *
import pgmapcss.db
import re

def compile_cond(func, param, eval_param):
    ret = '(' + param[1] + ' if eval_boolean([' + param[0] + ']' + eval_param + ') == \'true\''
    if len(param) > 2:
        ret += ' else ' + param[2]
    else:
        ret += " else ''"
    ret += ')'
    return ret

def load():
    eval_functions = Functions()

    eval_functions.register('add', op='+', math_level=3)
    eval_functions.register('and', op='&&', math_level=1)
    eval_functions.register('concat', op='.', math_level=6)
    eval_functions.register('contains', op='~=', math_level=7)
    eval_functions.register('differing', op=('!=', '<>'), math_level=7)
    eval_functions.register('div', op='/', math_level=4)
    eval_functions.register('equal', op='==', math_level=7)
    eval_functions.register('ge', op='>=', math_level=7)
    eval_functions.register('gt', op='>', math_level=7)
    eval_functions.register('identical', op=('===', 'eq'), math_level=7)
    eval_functions.register('le', op='<=', math_level=7)
    eval_functions.register('lt', op='<', math_level=7)
    eval_functions.register('mul', op='*', math_level=4)
    eval_functions.register('nonidentical', op=('!==', 'ne'), math_level=7)
    eval_functions.register('not', op='!', math_level=2)
    eval_functions.register('or', op='||', math_level=1)
    eval_functions.register('sub', op='-', math_level=1)
    eval_functions.register('cond', compiler=compile_cond)

    conn = pgmapcss.db.connection()

    for f in resource_listdir(__name__, ''):
        m = re.match('eval_(.*).py', f)
        if m:
            func = m.group(1)
            c = resource_string(__name__, f)
            c = c.decode('utf-8')
            eval_functions.register(func, src=c)

    return eval_functions
