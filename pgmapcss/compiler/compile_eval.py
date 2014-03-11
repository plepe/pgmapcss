import re
import pgmapcss.eval
eval_param = '' #, object, current, render_context'

def valid_func_name(func):
    if re.match('[a-zA-Z_0-9]+$', func):
        return func

    else:
        raise Exception('Illegal eval function name: ' + func)

def compile_eval(value, stat):
    global eval_param

    eval_functions = pgmapcss.eval.functions().list()

    if type(value) == str:
        if value[0:2] == 'v:':
            return repr(value[2:])
        elif value[0:2] == 'f:':
            func = value[2:]
            if not func in eval_functions:
                raise Exception('Unknown eval function: ' + func)
            return eval_functions[func].compiler([], eval_param, stat)
        else:
            raise Exception('compiling eval: ' + repr(value))

    if len(value) == 0:
        return ''

    if not value[0][0:2] in ('f:', 'o:'):
        return compile_eval(value[0], stat)

    param = [ compile_eval(i, stat) for i in value[1:] ]

    if value[0][0:2] == 'o:':
        func = [ k for k, v in eval_functions.items() if value[0][2:] in v.op ][0]

    elif value[0][0:2] == 'f:':
        func = value[0][2:]

    if not func in eval_functions:
        raise Exception('Unknown eval function: ' + func)
    return eval_functions[func].compiler(param, eval_param, stat)
