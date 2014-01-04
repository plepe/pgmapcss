def stat_all_scale_denominators(stat):
    return sorted(list(set([
            v['selectors']['min_scale']
            for v in stat['statements']
        ] + \
        [
            v['selectors']['max_scale']
            for v in stat['statements']
            if v['selectors']['max_scale'] != None
        ])),
        reverse=True)

def stat_properties(stat):
    return list(set([
        p['key']
        for v in stat['statements']
        for p in v['properties']
        if p['assignment_type'] == 'P'
    ]))

def stat_property_values(prop, stat):
    """Returns list of all values used on this property in any statement.
    Returns boolean 'True' if property is result of an eval expression."""
    return list(set([
        True if p['value_type'] == 'eval' else p['value']
        for v in stat['statements']
        for p in v['properties']
        if p['assignment_type'] == 'P' and p['key'] == prop
    ]))
