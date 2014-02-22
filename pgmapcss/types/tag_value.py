from .default import default

class tag_value(default):
    def compile(self, prop):
        return "current['tags'].get(" + repr(prop['value']) + ")"
