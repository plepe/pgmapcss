from .base import base

class default(base):
    def compile(self, prop):
        return repr(prop['value'])
