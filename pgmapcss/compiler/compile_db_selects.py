def filter_selectors(filter, stat):
    # where_selectors contains indexes of all selectors which we need for match queries
    where_selectors = []

    # get list of properties which are 'important' (create a symbol)
    style_element_properties = [
        k
        for i, j in stat['defines']['style_element_property'].items()
        for k in j['value'].split(';')
    ]

    # where_selectors: find list of selectors which are relevent for db where
    # matches (all that have an entry in @style_element_property)
    where_selectors += [
        i
        for i, v in enumerate(stat['statements'])
        for w in v['properties']
        if ((w['key'] in style_element_properties and w['assignment_type'] == 'P') or
            w['assignment_type'] == 'C') and
            v['selector']['min_scale'] <= filter['min_scale'] and
            (v['selector']['max_scale'] == None or v['selector']['max_scale'] >= filter['max_scale']) and
            not 'create_pseudo_element' in v['selector']
    ]

    # TODO combine

    # list of all tag assignments in form ( 'key', 'value', index of statement )
    # if value results of an eval statement use True instead
    list_tag_assignments = [
        (
            p['key'],
            True if p['value_type'] == 'eval' else p['value'],
            i 
        )
        for i, v in enumerate(stat['statements'])
        for p in v['properties'] if p['assignment_type'] == 'T'
        if v['selector']['min_scale'] <= filter['min_scale'] and
            (v['selector']['max_scale'] == None or v['selector']['max_scale'] >= filter['max_scale'])
    ]

    # uniq list
    return list(set(where_selectors))

def compile_db_selects(id, stat):
    ret = ''

    scale_denominators = stat.all_scale_denominators()

    max_scale = None
    for min_scale in scale_denominators:
        filter = { 'min_scale': min_scale, 'max_scale': max_scale or 10E+10}
        current_selectors = filter_selectors(filter, stat)

        # compile all selectors
        # TODO: define list of possible object_types
        conditions = [
            (
                object_type,
                stat['database'].compile_selector(stat['statements'][i], stat, prefix='', filter=filter, object_type=object_type)
            )
            for i in current_selectors
            for object_type in ({'node', 'way', 'area'} if stat['statements'][i]['selector']['type'] == True else { stat['statements'][i]['selector']['type'] })
        ]

        conditions = stat['database'].merge_conditions(conditions)

        max_scale = min_scale

        if ret == '':
            ret += 'if'
        else:
            ret += 'elif'

        ret += \
            ' render_context[\'scale_denominator\'] >= ' + str(min_scale) + ':\n' +\
            '    db_selects = ' + repr(conditions) + '\n'

    return ret
