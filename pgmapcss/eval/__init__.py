from .config import load
from .possible_values import possible_values

eval_functions = None

def functions(stat=None):
    global eval_functions

    if eval_functions is None or (stat is not None and eval_functions.stat != stat):
        eval_functions = load(stat)

    return eval_functions
