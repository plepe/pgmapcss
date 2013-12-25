from .compile_function import compile_function

def compile_style(id, stat):
    ret = {}

    ret['function'] = compile_function(id, stat)

    return ret
