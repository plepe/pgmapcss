from .functions import Functions
from pkg_resources import *
import pgmapcss.db
import re

def load(stat):
    eval_functions = Functions(stat)

    conn = pgmapcss.db.connection()

    for f in resource_listdir(__name__, ''):
        m = re.match('eval_(.*).py', f)
        if m:
            func = m.group(1)
            c = resource_string(__name__, f)
            c = c.decode('utf-8')
            eval_functions.register(func, src=c)

    return eval_functions
