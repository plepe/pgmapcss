from .functions import Functions
from pkg_resources import *
import pgmapcss.db
import re

def compile_cond(func, param, eval_param, stat):
    ret = '(' + param[1] + ' if eval_boolean([' + param[0] + ']' + eval_param + ') == \'true\''
    if len(param) > 2:
        ret += ' else ' + param[2]
    else:
        ret += " else ''"
    ret += ')'
    return ret

def compile_style_id(func, param, eval_param, stat):
    return repr(stat['id']);

def load():
    eval_functions = Functions()

    eval_functions.register('cond', compiler=compile_cond)
    eval_functions.register('style_id', compiler=compile_style_id)

    conn = pgmapcss.db.connection()

    for f in resource_listdir(__name__, ''):
        m = re.match('eval_(.*).py', f)
        if m:
            func = m.group(1)
            c = resource_string(__name__, f)
            c = c.decode('utf-8')
            eval_functions.register(func, src=c)

    return eval_functions
