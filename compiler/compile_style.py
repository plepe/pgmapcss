from .compile_function import compile_function

def compile_style(id, stat):
    ret = {}

# find list of pseudo elements
    stat['pseudo_elements'] = list(set(
        [ (i['selectors']['pseudo_element']) for i in stat['statements'] ]
    ))
    ret['function'] = compile_function(id, stat)

    return ret
