from .compile_eval import compile_eval

def compile_pseudo_class_condition(condition, stat):
    if condition['key'] in ('active', 'hover'):
        return ['False']

    elif condition['key'] == 'closed':
        return [compile_eval('f:is_closed', condition, stat) + " == 'true'"]

    else:
        print('unknown/unsupported pseudo class: {key}'.format(**condition))
        return ['False']
