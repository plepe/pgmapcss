class config_eval_parent_tag(config_base):
    def possible_values(self, param_values, prop, stat):
        options = { 'requirements': set () }
        if param_values[0] in ['osm:version', 'osm:user_id', 'osm:user', 'osm:timestamp', 'osm:changeset']:
            options['requirements'].add('meta')

        return ( { True, '' }, 0, options )

def eval_parent_tag(param, current):
    for p in param:
        if p in current['parent_object']['tags']:
            return current['parent_object']['tags'][p]

    return ''
