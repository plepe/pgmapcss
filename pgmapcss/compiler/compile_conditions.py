from .compile_condition import compile_condition

def compile_conditions(conditions, stat, var=''):
    ret = []

    for i in conditions:
        c = compile_condition(i, stat, var=var)
        if c:
            ret += c

    return ret
