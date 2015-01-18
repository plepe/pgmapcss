from .compile_eval import compile_eval

def compile_pseudo_class_action(condition, statement, stat, indent=''):
    if condition['key'] in ('active', 'hover', 'closed', 'connection', 'unconnected', 'tagged', 'righthandtraffic', 'lefthandtraffic', 'lang'):
        return ''

    if condition['key'] in ('order-natural-asc', 'order-natural-desc', 'order-alphabetical-asc', 'order-alphabetical-desc', 'order-numerical-asc', 'order-numerical-desc'):
        ret = indent + "yield (" + repr(condition['key']) + ", " + repr(statement['id']) + ", "
        if condition['value_type'] == 'eval':
            ret += compile_eval(condition['value'], condition, stat)
        else:
            ret += "current['tags'][" + repr(condition['value']) + "] if " + repr(condition['value']) + " in current['tags'] else None"

        ret += ')\n'

        return ret

    return ''

def compile_pseudo_class_actions(selector, statement, stat, indent=''):
    ret = ''

    for condition in selector['conditions']:
        if condition['op'] == 'pseudo_class':
            ret += compile_pseudo_class_action(condition, statement, stat, indent)

    return ret
