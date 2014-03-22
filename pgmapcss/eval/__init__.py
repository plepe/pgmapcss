from .config import load
from .possible_values import possible_values

eval_functions = None

def functions():
    global eval_functions

    if eval_functions is None:
        eval_functions = load()

    return eval_functions
