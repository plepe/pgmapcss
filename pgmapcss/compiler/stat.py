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

def stat_property_values(prop, stat, include_illegal_values=False, value_type=None, pseudo_element=None):
    """Returns set of all values used on this property in any statement.
    Returns boolean 'True' if property is result of an eval expression."""
    values = {
        True if p['value_type'] == 'eval' else p['value']
        for v in stat['statements']
        for p in v['properties']
        if pseudo_element == None or v['selector']['pseudo_element'] in ('*', pseudo_element)
        if p['assignment_type'] == 'P' and p['key'] == prop
        if value_type == None or value_type == p['value_type']
    }

    if 'default_other' in stat['defines'] and prop in stat['defines']['default_other']:
        other = stat['defines']['default_other'][prop]['value']
        other = stat_property_values(other, stat, include_illegal_values, value_type, pseudo_element)
        values = values.union(other)

    if include_illegal_values:
        return values

    if 'values' in stat['defines'] and prop in stat['defines']['values']:
        allowed_values = stat['defines']['values'][prop]['value'].split(';')

        if True in values:
            values = values.union(allowed_values)

        values = {
            v if v in allowed_values else allowed_values[0]
            for v in values
        }

    values = {
        v
        for v in values
        if v != None
    }

    return values
