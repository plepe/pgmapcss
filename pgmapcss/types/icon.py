from .default import default

class icon(default):
    def compile(self, prop):
        if os.path.exists(prop['value']):
            return repr(prop['value'])

        else:
            return repr("icon:" + prop['value'])
