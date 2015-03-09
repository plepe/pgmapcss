class config_eval_tag(config_base):
    def possible_values(self, param_values, prop, stat):
        if not 'statement' in prop or \
             not 'selector' in prop['statement'] or \
             not 'pseudo_element' in prop['statement']['selector']:
            return ( { True, '' }, 0 )

        if not 'id' in prop:
            return ( { True, '' }, 0 )

        values = set()
        for p in param_values:
            values = values.union(stat.property_values(p, max_prop_id=prop['id'] - 1, include_none=True, assignment_type='T'))

        # convert None to ''
        values = {
            '' if v is None else v
            for v in values
        }

        # tag() may always return ''
        values.add('')

        # tag() may always return any value, short of when the tag name starts with a '.'
        if True in [ p[0] != '.' for p in param_values ]:
            values.add(True)

        return ( values, 0 )

def eval_tag(param):
    for p in param:
        if p in current['tags']:
            v = current['tags'][p]
            if not v is None:
                return v

    return ''

# IN ['name']
# OUT 'Foobar'
# IN ['ref', 'name']
# OUT 'Foobar'
# IN ['ref']
# OUT ''
