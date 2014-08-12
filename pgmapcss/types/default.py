class default:
    def __init__(self, key, stat):
        self.key = key
        self.stat = stat

    def compile_check(self, value):
        return value

    def compile(self, prop):
        return repr(prop['value'])

    def compile_postprocess(self):
        return None

    def stat_postprocess(self, values, pseudo_element=None):
        pass

    def stat_value(self, prop):
        return prop['value']

    def stat_all_values(self):
        return {True}

    def get_global_data(self):
        pass
