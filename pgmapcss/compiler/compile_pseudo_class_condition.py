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

    elif condition['key'] == 'tagged':
        return ["len({ k: v for k, v in current['tags'].items() if not re.match('(source.*|note|comment|converted_by|created_by|watch.*|fixme|FIXME|description|attribution)$', k) }) != 0"]

    elif condition['key'] == 'righthandtraffic':
        return [compile_eval('f:is_right_hand_traffic', condition, stat) + " != 'false'"]

    elif condition['key'] == 'lefthandtraffic':
        return [compile_eval('f:is_left_hand_raffic', condition, stat) + " != 'false'"]

    else:
        print('unknown/unsupported pseudo class: {key}'.format(**condition))
        return ['False']
