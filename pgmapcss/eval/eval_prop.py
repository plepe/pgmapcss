class config_eval_prop(config_base):
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

        values = pgmapcss.compiler.stat.stat_property_values(param_values[0], stat, pseudo_element=pseudo_element, max_prop_id=prop['id'] - 1)
        return ( values, 0 )

def eval_prop(param):
    if len(param) == 0:
        return ''

    pseudo_element = current['pseudo_element']

    if len(param) > 1:
        pseudo_element = param[1]

    if pseudo_element not in current['properties']:
        return ''

    if param[0] in current['properties'][pseudo_element]:
        return current['properties'][pseudo_element][param[0]]
    else:
        return ''

# TESTS
# IN ['width']
# OUT '2'
# IN ['width', 'test']
# OUT ''
# IN ['fill-color', 'test']
# OUT '#00ff00'
# IN ['width', 'foobar']
# OUT ''
