from .base import base

class icon(base):
    def compile(self, prop):
        if os.path.exists(prop['value']):
            return repr(prop['value'])

        else:
            return repr("icon:" + prop['value'])
