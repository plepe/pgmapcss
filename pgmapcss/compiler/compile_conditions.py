from .compile_condition import compile_condition

def compile_conditions(conditions, stat, var=''):
    ret = []

    for i in conditions:
        c = compile_condition(i, stat, var=var)
        if c:
            ret.append(c)

    if len(ret) == 0:
        return 'True'

    return ' and '.join(ret)
