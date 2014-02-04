from .compile_function_match import compile_function_match

def compile_style(id, stat):
    ret = {}

# find list of pseudo elements
    stat['pseudo_elements'] = list({
        i['selector']['pseudo_element']
        for i in stat['statements']
        if i['selector']['pseudo_element'] != '*'
    })
    ret['function_match'] = compile_function_match(id, stat)

    return ret
