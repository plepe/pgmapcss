from .compile_function_check import compile_function_check
from .compile_function_get_where import compile_function_get_where
from .compile_function_match import compile_function_match

def compile_style(id, stat):
    ret = {}

# find list of pseudo elements
    stat['pseudo_elements'] = list(set(
        [ (i['selectors']['pseudo_element']) for i in stat['statements'] ]
    ))
    ret['function_check'] = compile_function_check(id, stat)
    ret['function_get_where'] = compile_function_get_where(id, stat)
    ret['function_match'] = compile_function_match(id, stat)

    return ret
