import pgmapcss.eval

def possible_values(value, stat):
    global eval_param

    eval_functions = pgmapcss.eval.functions().list()

    if type(value) == str:
        if value[0:2] == 'v:':
            return { value[2:] }
        elif value[0:2] == 'f:':
            func = value[2:]
            if not func in eval_functions:
                raise Exception('Unknown eval function: ' + func)
            r = eval_functions[func].possible_values([], stat)
            if type(r) == set:
                return r
            else:
                return { r }
        else:
            raise Exception('compiling eval: ' + repr(value))

    if len(value) == 0:
        return {}

    if not value[0][0:2] in ('f:', 'o:'):
        return possible_values(value[0], stat)

    param = [ possible_values(i, stat) for i in value[1:] ]

    if value[0][0:2] == 'o:':
        func = [ k for k, v in eval_functions.items() if value[0][2:] in v.op ][0]

    elif value[0][0:2] == 'f:':
        func = value[0][2:]

    if not func in eval_functions:
        raise Exception('Unknown eval function: ' + func)

    # make sure all elements are sets
    param = [ {p} if type(p) == str else p for p in param ]
    # build all possible combinations of input parameters
    combinations = [[]]
    for p in param:
        new_combinations = []
        for combination in combinations:
            for v in p:
                c = list(combination) # copy original list
                c.append(v)
                new_combinations.append(c)
        combinations = new_combinations

    # finally calculate possible results
    result = {
        eval_functions[func].possible_values(param, stat)
        for param in combinations
        if not True in param
    }

    # if any of the combinations contains a 'True' value, add True to the
    # return values too
    if True in [ True for param in combinations if True in param ]:
        result.add(True)

    return result
