import copy

# takes a statement as input and returns several selectors with condition
# combinations from set statements. also, conditions with a key prefixed by '.'
# are removed.
def resolve_set_statements(statement, done, stat):
    # if as type a wildcard was given ('*'), run resolve_set_statements with
    # all possible types
    if statement['selector']['type'] is True:
        ret = []

        for r in [ 'node', 'way', 'relation', 'multipolygon' ]:
            s = copy.deepcopy(statement)
            s['selector']['type'] = r
            ret += resolve_set_statements(s, done, stat)
            done.remove(s['id'])

        return ret

    # initialize return selector(s) with empty conditions
    ret = copy.deepcopy(statement['selector'])
    ret['conditions'] = []
    ret = [ ret ]

    if statement['id'] in done:
        return ret
    done.append(statement['id'])

    # iterate over all conditions in the statement
    for condition in statement['selector']['conditions']:
        last_ret = ret
        ret = []

        # check if there are any statements which assign the current condition key
        filter = {
            'has_set_tag': condition['key'],
            'max_id': statement['id'],
            'min_scale': statement['selector']['min_scale'],
            'max_scale': statement['selector']['max_scale'] or 10E+10,
        }
        set_statements = stat.filter_statements(filter)

        # recurse into resolve_set_statements, to also resolve conditions in
        # the statements where set statements happened
        set_statements = [
            resolve_set_statements(s, done, stat)
            for s in set_statements
        ]

        # for all set statements create a new set of conditions
        for lr in last_ret:
            for s1 in set_statements:
                for s in s1:
                    r = copy.deepcopy(lr)
                    r['conditions'] += s['conditions']

                    # also copy parent selector from set statements (but only,
                    # if there's not a parent selector on the child yet)
                    # TODO: allow several parent selectors for a single selector
                    if 'parent' in s and not 'parent' in r:
                        r['parent'] = s['parent']
                        r['link'] = s['link']

                    ret.append(r)

        # for each set of conditions add the current condition
        # unless the condition's key does not start with a '.'
        if condition['key'][0] != '.':
            for r in last_ret:
                c = copy.deepcopy(r)
                r['conditions'] += [ condition ]
                ret.append(r)

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

def check_is_sub_selector(selector, master_selector):
    # if master_selector has relationship conditions, check if these match with
    # the current selectors conditions
    if 'parent' in master_selector:
        if not 'parent' in selector:
            return False

        if selector['link']['type'] != master_selector['link']['type'] or\
            not check_is_sub_selector(selector['link'], master_selector['link']) or\
            not check_is_sub_selector(selector['parent'], master_selector['parent']):
                return False

    # check if all the master_conditions are also in current selector's
    # condition
    is_sub = True
    for c in master_selector['conditions']:
        if not c in selector['conditions']:
            # also check for has_tag conditions
            has_tag = False
            if c['op'] == 'has_tag':
                for oc in selector['conditions']:
                    if oc['op'] not in ('key_regexp', 'eval') and \
                       oc['key'] == c['key']:
                        has_tag = True

            if not has_tag:
                is_sub = False
                break

    return is_sub

def compile_selectors_db(statements, selector_index, stat, filter=None):
    selectors = {}

    for i in statements:
        if type(i) == int:
            _statement = stat['statements'][i]
        else:
            _statement = i

        if filter:
            _statement = copy.deepcopy(_statement)
            _statement['selector']['min_scale'] = filter['min_scale']
            _statement['selector']['max_scale'] = filter['max_scale']

        for selector in resolve_set_statements(_statement, [], stat):
            if selector_index is not None:
                selector = selector[selector_index]

            # make sure that selector does not get modified
            selector = copy.deepcopy(selector)

            if not selector['type'] in selectors:
                selectors[selector['type']] = []

            # check if the current selector is a sub selector of any other ->
            # then we don't need to add it
            is_sub = False
            for s in selectors[selector['type']]:
                if check_is_sub_selector(selector, s):
                    is_sub = True
                    break

            if not is_sub:
                # check if the current selector is a master selector of others
                # -> remove those
                selectors[selector['type']] = [
                    s
                    for s in selectors[selector['type']]
                    if not check_is_sub_selector(s, selector)
                ]

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

        conditions = compile_selectors_db(current_selectors, None, stat, filter)

        max_scale = min_scale

        if ret == '':
            ret += 'if'
        else:
            ret += 'elif'

        ret += \
            ' render_context[\'scale_denominator\'] >= ' + str(min_scale) + ':\n' +\
            '    db_selects = ' + repr(conditions) + '\n'

    return ret
