from .compile_function import compile_function
from .compile_get_where import compile_get_where

def compile_style(id, stat):
    ret = {}

# find list of pseudo elements
    stat['pseudo_elements'] = list(set(
        [ (i['selectors']['pseudo_element']) for i in stat['statements'] ]
    ))
    ret['function'] = compile_function(id, stat)
    ret['get_where'] = compile_get_where(id, stat)

    return ret
