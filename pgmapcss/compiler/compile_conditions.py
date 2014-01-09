from .compile_condition import compile_condition

def compile_conditions(conditions, stat, prefix=''):
    ret = []

    for i in conditions:
        c = compile_condition(i, stat, prefix=prefix)
        if c:
            ret.append(c)

    if len(ret) == 0:
        return 'true'

    return ' and '.join(ret)
