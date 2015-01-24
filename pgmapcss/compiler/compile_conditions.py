from .compile_condition import compile_condition
import pgmapcss.eval.merge_options
import copy

def compile_conditions(conditions, stat, var=''):
    ret = []

    for i in conditions:
        result = compile_condition(i, stat, var=var)
        if result:
            for c in result['code']:
                r = copy.deepcopy(result)
                r['code'] = c
                ret.append(r)

    return ret
