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
            return 'eval_' + valid_func_name(value[2:]) + '(\'[]\'' + eval_param + ')'
        else:
            raise Exception('compiling eval: ' + repr(value))

    if len(value) == 0:
        return ''

    if not value[0][0:2] in ('f:', 'o:'):
        return compile_eval(value[0], stat)

    param = [ compile_eval(i, stat) for i in value[1:] ]

    if value[0][0:2] == 'o:':
        func = [ k for k, v in eval_functions.items() if 'op' in v and value[0][2:] in v['op'] ][0]

    elif value[0][0:2] == 'f:':
        func = value[0][2:]

    if func in eval_functions and 'compiler' in eval_functions[func]:
        return eval_functions[func]['compiler'](func, param, eval_param, stat)

    else:
        return 'eval_' + valid_func_name(func) + '([' + ', '.join(param) + ']' + eval_param + ')'
