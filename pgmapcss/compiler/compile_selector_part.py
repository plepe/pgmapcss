from .compile_conditions import compile_conditions

def compile_selector_part(selector, stat, prefix="current"):
    ret = []

    if selector['type'] != True:
        ret.append(repr(selector['type']) + " in current['types']")

    ret.append(compile_conditions(selector['conditions'], stat, var="current['tags']"))

    if len(ret) == 0:
        return 'True'

    return ' and '.join(ret)
