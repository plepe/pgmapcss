from .base import base

class tag_value(base):
    def compile(self, prop):
        return "current['tags'].get(" + repr(prop['value']) + ")"
