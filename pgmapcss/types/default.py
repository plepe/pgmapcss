class default:
    def __init__(self, key, stat):
        self.key = key
        self.stat = stat

    def compile_check(self, value):
        return value

    def compile(self, prop):
        return repr(prop['value'])

    def stat_value(self, prop):
        return prop['value']

    def includes(self):
        return {}

#    def __str__(self):
#        pass
