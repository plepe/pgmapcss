from .default import default
import re

class angle(default):
    def stat_value(self, prop):
        if prop['value'] is None:
            return None

        m = re.match('(\-?[0-9]+(\.[0-9]+)?)$', prop['value'])
        if m:
            return m.group(1)

        return None
