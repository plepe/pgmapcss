from .default import default

class tag_value(default):
    def compile(self, prop):
        if prop['value_type'] == 'string':
            return repr(prop['value'])

        return "current['tags'].get(" + repr(prop['value']) + ")"

    def stat_value(self, prop):
        if prop['value_type'] == 'string':
            return prop['value']

        # value is read from current object tag -> we can't predict
        return True
