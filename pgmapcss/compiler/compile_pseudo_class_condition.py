from .compile_eval import compile_eval

def compile_pseudo_class_condition(condition, stat):
    if condition['key'] in ('active', 'hover'):
        return ['False']

    elif condition['key'] == 'closed':
        return [compile_eval('f:is_closed', condition, stat) + " == 'true'"]

    elif condition['key'] == 'connection':
        return ["len(list(objects_member_of(current['object']['id'], 'way', None))) > 1"]

    elif condition['key'] == 'unconnected':
        return ["len(list(objects_member_of(current['object']['id'], 'way', None))) == 0"]

    else:
        print('unknown/unsupported pseudo class: {key}'.format(**condition))
        return ['False']
