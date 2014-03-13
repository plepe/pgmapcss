import pgmapcss.eval

def possible_values(value, stat):
    global eval_param

    eval_functions = pgmapcss.eval.functions().list()

    if type(value) == str:
        if value[0:2] == 'v:':
            return value[2:]
        elif value[0:2] == 'f:':
            func = value[2:]
            if not func in eval_functions:
                raise Exception('Unknown eval function: ' + func)
            return eval_functions[func].possible_values([], stat)
        else:
            raise Exception('compiling eval: ' + repr(value))

    if len(value) == 0:
        return None

    if not value[0][0:2] in ('f:', 'o:'):
        return _possible_values(value[0], stat)

    param = [ possible_values(i, stat) for i in value[1:] ]
    if True in param:
        return True

    if value[0][0:2] == 'o:':
        func = [ k for k, v in eval_functions.items() if value[0][2:] in v.op ][0]

    elif value[0][0:2] == 'f:':
        func = value[0][2:]

    if not func in eval_functions:
        raise Exception('Unknown eval function: ' + func)

    return eval_functions[func].possible_values(param, stat)
