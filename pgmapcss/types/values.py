from .default import default

class values(default):
    def __init__(self, key, stat):
        super().__init__(key, stat)
        self.values = stat['defines']['values'][key]['value'].split(';')

    def compile(self, prop):
        return repr(self.stat_value(prop))

    def stat_value(self, prop):
        if prop['value'] in self.values:
            return prop['value']

        return self.values[0]

    def stat_all_values(self):
        return self.values
