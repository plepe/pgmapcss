from .compile_eval import compile_eval

def compile_pseudo_class_condition(condition, stat):
    if condition['key'] in ('order-natural-asc', 'order-natural-desc', 'order-alphabetical-asc', 'order-alphabetical-desc', 'order-numerical-asc', 'order-numerical-desc'):
        return { 'code': ['True'] }

    if condition['key'] not in ('active', 'hover', 'closed', 'connection', 'unconnected', 'tagged', 'righthandtraffic', 'lefthandtraffic', 'lang'):
        print('unknown/unsupported pseudo class: {key}'.format(**condition))
        return { 'code': ['False'] }

    if 'value' in condition and condition['key'] not in ('lang',):
        print('pseudo class {key} does not accept a parameter -> ignoring'.format(**condition))
        return { 'code': ['False'] }

    if condition['key'] in ('active', 'hover'):
        return { 'code': ['False'] }

    elif condition['key'] == 'closed':
        result = compile_eval('f:is_closed', condition, stat)
        result['code'] = [result['code'] + " == 'true'"]
        return result

    elif condition['key'] == 'connection':
        return { 'code': ["len(list(objects_member_of(current['object']['id'], 'way', None))) > 1"] }

    elif condition['key'] == 'unconnected':
        return { 'code': ["len(list(objects_member_of(current['object']['id'], 'way', None))) == 0"] }

    elif condition['key'] == 'tagged':
        return { 'code': ["len({ k: v for k, v in current['tags'].items() if not re.match('(source.*|note|comment|converted_by|created_by|watch.*|fixme|FIXME|description|attribution)$', k) }) != 0"] }

    elif condition['key'] == 'righthandtraffic':
        result = compile_eval('f:is_right_hand_traffic', condition, stat)
        result['code'] = [ result['code'] + " != 'false'"]
        return result

    elif condition['key'] == 'lefthandtraffic':
        result = compile_eval('f:is_left_hand_raffic', condition, stat)
        result['code'] = [ result['code'] + " != 'false'"]
        return result

    elif condition['key'] == 'lang':
        if not 'value' in condition:
            print('pseudo class :lang() requires a parameter -> ignoring'.format(**condition))
            return { 'code': ['False'] }

        if condition['value_type'] == 'eval':
            result = compile_eval(condition['value'], condition, stat)
            result['code'] = ["parameters['lang'] in " + code + ".split(';')"]
            return result
        else:
            return { 'code': ["parameters['lang'] in " + repr(condition['value'].split(';'))] }
