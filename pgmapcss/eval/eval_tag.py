class config_eval_tag(config_base):
    def possible_values(self, param_values, prop, stat):
        options = { 'requirements': set () }
        if param_values[0] in ['osm:version', 'osm:user_id', 'osm:user', 'osm:timestamp', 'osm:changeset']:
            options['requirements'].add('meta')

        return ( { True, '' }, 0, options )

def eval_tag(param, current):
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
