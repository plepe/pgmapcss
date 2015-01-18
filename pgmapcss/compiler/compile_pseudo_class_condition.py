from .compile_eval import compile_eval

def compile_pseudo_class_condition(condition, stat):
    if condition['key'] in ('order-natural-asc', 'order-natural-desc', 'order-alphabetical-asc', 'order-alphabetical-desc', 'order-numerical-asc', 'order-numerical-desc'):
        return ['True']

    if condition['key'] not in ('active', 'hover', 'closed', 'connection', 'unconnected', 'tagged', 'righthandtraffic', 'lefthandtraffic', 'lang'):
        print('unknown/unsupported pseudo class: {key}'.format(**condition))
        return ['False']

    if 'value' in condition and condition['key'] not in ('lang',):
        print('pseudo class {key} does not accept a parameter -> ignoring'.format(**condition))
        return ['False']

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

    elif condition['key'] == 'lang':
        if not 'value' in condition:
            print('pseudo class :lang() requires a parameter -> ignoring'.format(**condition))
            return ['False']

        if condition['value_type'] == 'eval':
            return ["parameters['lang'] in " + compile_eval(condition['value'], condition, stat) + ".split(';')"]
        else:
            return ["parameters['lang'] in " + repr(condition['value'].split(';'))]
