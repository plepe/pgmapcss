import pgmapcss.types
import pgmapcss.eval

def stat_all_scale_denominators(stat):
    return sorted(list(set([
            v['selector']['min_scale']
            for v in stat['statements']
        ] + \
        [
            v['selector']['max_scale']
            for v in stat['statements']
            if v['selector']['max_scale'] != None
        ])),
        reverse=True)

def stat_properties(stat):
    return list(set([
        p['key']
        for v in stat['statements']
        for p in v['properties']
        if p['assignment_type'] == 'P'
    ]))

def stat_property_values(prop, stat, pseudo_element=None, include_illegal_values=False, value_type=None, eval_true=True, max_prop_id=None):
    """Returns set of all values used on this property in any statement.
    Returns boolean 'True' if property is result of an unresolveable eval
    expression.

    Parameters:
    pseudo_element: limit returned values to given pseudo_element (default: None which means all)
    include_illegal_values: If True all values as given in MapCSS are returned, if False the list is sanitized (see @values). Default: False
    value_type: Only values with value_type will be returned. Default None (all)
    eval_true: Return 'True' for values which result of an unresolvable eval expression. Otherwise this value will be removed. Default: True.
    max_prop_id: evaluate only properties with an id <= max_prop_id
    """
    prop_type = pgmapcss.types.get(prop, stat)

    # go over all statements and their properties and collect it's values. If
    # include_illegal_values==False sanitize list. Do not include eval
    # statements.
    values = {
        p['value'] if include_illegal_values else prop_type.stat_value(p)
        for v in stat['statements']
        for p in v['properties']
        if pseudo_element == None or v['selector']['pseudo_element'] in ('*', pseudo_element)
        if p['assignment_type'] == 'P' and p['key'] == prop
        if value_type == None or value_type == p['value_type']
        if p['value_type'] != 'eval'
        if max_prop_id is None or p['id'] <= max_prop_id
    }

    # resolve eval functions (as far as possible) - also sanitize list.
    if True:
        values = values.union({
            v1 if v1 == True or include_illegal_values else prop_type.stat_value({
                'value_type': 'eval',
                'value': v1
            })
            for v in stat['statements']
            for p in v['properties']
            if pseudo_element == None or v['selector']['pseudo_element'] in ('*', pseudo_element)
            if p['assignment_type'] == 'P' and p['key'] == prop
            if p['value_type'] == 'eval'
            if max_prop_id is None or p['id'] <= max_prop_id
            for v1 in pgmapcss.eval.possible_values(p['value'], p, stat)[0]
        })

    if 'default_other' in stat['defines'] and prop in stat['defines']['default_other']:
        other = stat['defines']['default_other'][prop]['value']
        other = stat_property_values(other, stat, pseudo_element, include_illegal_values, value_type, eval_true, max_prop_id)
        values = values.union(other)

    if 'generated_properties' in stat and prop in stat['generated_properties']:
        gen = stat['generated_properties'][prop]
        combinations = stat_properties_combinations(gen[0], stat, pseudo_element, include_illegal_values, value_type, eval_true, max_prop_id)
        values = values.union({
            gen[1](combination, stat)
            for combination in combinations
        })

    if include_illegal_values:
        return values

    if True in values:
        values.remove(True)
        values = values.union(prop_type.stat_all_values())

    values = {
        v
        for v in values
        if v != None
    }

    if True in values:
        if not 'unresolvable_properties' in stat:
            stat['unresolvable_properties'] = set()
        stat['unresolvable_properties'].add(prop)

    if not eval_true and True in values:
        values.remove(True)

    return values

def stat_properties_combinations_pseudo_element(keys, stat, pseudo_element, include_illegal_values=False, value_type=None, eval_true=True, max_prop_id=None):
    combinations_list = [{}]

    for k in keys:
        new_combinations_list = []

        for combination in combinations_list:
            for v in stat_property_values(k, stat, pseudo_element, include_illegal_values, value_type, eval_true, max_prop_id):
                c = combination.copy()
                c[k] = v
                new_combinations_list.append(c)

        combinations_list = new_combinations_list

    return combinations_list

def stat_properties_combinations(keys, stat, pseudo_elements=None, include_illegal_values=False, value_type=None, eval_true=True, max_prop_id=None):
    combinations = []
    if type(pseudo_elements) == str:
        pseudo_elements = [ pseudo_elements ]
    if pseudo_elements is None:
        pseudo_elements = stat['pseudo_elements']

    for pseudo_element in pseudo_elements:
        combinations += stat_properties_combinations_pseudo_element(keys, stat, pseudo_element, include_illegal_values, value_type, eval_true, max_prop_id)

    ret = []
    for combination in combinations:
        if not combination in ret:
            ret += [ combination ]

    return ret

def stat_add_generated_property(key, keys, fun, stat):
    if not 'generated_properties' in stat:
        stat['generated_properties'] = {}

    stat['generated_properties'][key] = ( keys, fun )
