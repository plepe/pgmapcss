from .config import load

eval_functions = None

def functions():
    global eval_functions

    if eval_functions is None:
        eval_functions = load()

    return eval_functions
