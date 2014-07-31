class config_eval_is_prop_set(config_base):
    def possible_values(self, param_values, prop, stat):
        import pgmapcss.compiler.stat

        if len(param_values) > 1:
            pseudo_element = param_values[1]
        elif not 'statement' in prop or \
             not 'selector' in prop['statement'] or \
             not 'pseudo_element' in prop['statement']['selector']:
            return ( True, 0 )
        else:
            pseudo_element = prop['statement']['selector']['pseudo_element']

        if not 'id' in prop:
            return ( True, 0 )

        keys = stat.properties(param_values[0], pseudo_element=pseudo_element, max_prop_id=prop['id'] - 1)

        return ( param_values[0] in keys, 0 )

def eval_is_prop_set(param):
    if len(param) == 0:
        return ''

    pseudo_element = current['pseudo_element']

    if len(param) > 1:
        pseudo_element = param[1]

    if pseudo_element not in current['properties']:
        return ''

    if param[0] in current['properties'][pseudo_element]:
        return 'true'
    else:
        return 'false'

# TESTS
# IN ['width']
# OUT 'true'
# IN ['width', 'test']
# OUT 'false'
# IN ['fill-color', 'test']
# OUT 'true'
# IN ['width', 'foobar']
# OUT ''
