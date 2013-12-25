from .compile_statement import compile_statement

def compile_function(id, stat):
    ret = ''

    stat['properties_values'] = {}

    for i in stat['statements']:
        ret += compile_statement(i, stat)

    return ret
