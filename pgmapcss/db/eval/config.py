from .functions import Functions
import pgmapcss.db

eval_functions = None

def compile_cond(func, param, eval_param):
    ret = '(CASE WHEN eval_boolean(Array[' + param[0] + ']' + eval_param + ') = \'true\' THEN ' + param[1]
    if len(param) > 2:
        ret += ' ELSE ' + param[2]
    ret += ' END)'
    return ret

def load():
    global eval_functions
    if eval_functions:
        return eval_functions

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
    res = conn.prepare("select proname from pg_catalog.pg_namespace n join pg_catalog.pg_proc p on pronamespace = n.oid where nspname = any (current_schemas(false)) and proname similar to 'eval_%'")()
    [ eval_functions.register(r[0][5:]) for r in res ]


    return eval_functions.list()
