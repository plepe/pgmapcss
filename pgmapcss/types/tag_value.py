from .default import default

class tag_value(default):
    def compile(self, prop):
        if prop['value_type'] == 'string':
            return repr(prop['value'])

        # TODO: first priority should name "name:" + LANG
        if prop['value'] == 'auto' and \
            (prop['key'] == 'text' or prop['key'][-5:] == '-text'):
            return "current['tags'].get('name') or " +\
                   "current['tags'].get('int_name') or " +\
                   "current['tags'].get('ref') or " +\
                   "current['tags'].get('operator') or " +\
                   "current['tags'].get('brand') or " +\
                   "current['tags'].get('addr:housenumber')"

        return "current['tags'].get(" + repr(prop['value']) + ")"

    def stat_value(self, prop):
        if prop['value_type'] == 'string':
            return prop['value']

        # value is read from current object tag -> we can't predict
        return True
