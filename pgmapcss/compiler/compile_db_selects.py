import copy

# takes a list of conditions as input and returns several condition combinations
def resolve_set_statements(statement, done, stat):
    ret = [ [] ]
    if statement['id'] in done:
        return [ [] ]
    done.append(statement['id'])

    # iterate over all conditions in the statement
    for condition in statement['selector']['conditions']:
        last_ret = ret
        ret = []

        # check if there are any statements which assign the current condition key
        filter = {
            'has_set_tag': condition['key'],
            'max_id': statement['id']
        }
        set_statements = stat.filter_statements(filter)

        # recurse into resolve_set_statements, to also resolve conditions in
        # the statements where set statements happened
        set_statements = [
            resolve_set_statements(s, done, stat)
            for s in set_statements
        ]

        # for all set statements create a new set of conditions
        ret = [
            r + s1
            for r in last_ret
            for s in set_statements
            for s1 in s
        ]

        # for each set of conditions add the current condition
        # unless the condition's key does not start with a '.'
        if condition['key'][0] != '.':
            ret += [
                r + [ condition ]
                for r in last_ret
            ]

    return ret

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

def compile_selectors_db(statements, selector_index, stat):
    selectors = {}

    for i in statements:
        if type(i) == int:
            _statement = copy.deepcopy(stat['statements'][i])
        else:
            _statement = copy.deepcopy(i)

        for c in resolve_set_statements(_statement, [], stat):
            _statement['selector']['conditions'] = c
            if selector_index is None:
                selector = _statement['selector']
            else:
                selector = _statement['selector'][selector_index]

            if not selector['type'] in selectors:
                selectors[selector['type']] = []

            selectors[selector['type']].append(selector)

    # compile each selector
    conditions = {
        t: [
            stat['database'].compile_selector(selector)
            for selector in s
        ]
        for t, s in selectors.items()
    }

    # compile all selectors
    # TODO: define list of possible object_types
    # TODO: how to handle wildcard object type?

    # remove all invalid conditions from list
    conditions = {
        t: [
            c
            for c in cs
            if c != False
        ]
        for t, cs in conditions.items()
    }

    # merge all conditions for each types together
    conditions = {
            t: stat['database'].merge_conditions(cs)
            for t, cs in conditions.items()
        }

    # remove False entries
    conditions = {
            t: cs
            for t, cs in conditions.items()
            if cs is not False
        }

    return conditions

def compile_db_selects(id, stat):
    ret = ''

    scale_denominators = stat.all_scale_denominators()

    max_scale = None
    for min_scale in scale_denominators:
        filter = { 'min_scale': min_scale, 'max_scale': max_scale or 10E+10}
        current_selectors = filter_selectors(filter, stat)

        conditions = compile_selectors_db(current_selectors, None, stat)

        max_scale = min_scale

        if ret == '':
            ret += 'if'
        else:
            ret += 'elif'

        ret += \
            ' render_context[\'scale_denominator\'] >= ' + str(min_scale) + ':\n' +\
            '    db_selects = ' + repr(conditions) + '\n'

    return ret
