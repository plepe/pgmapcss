from .default import default
import os
from wand.image import Image

class icon(default):
    def __init__(self, key, stat):
        default.__init__(self, key, stat)
        self.icons = {}

    def compile(self, prop):
        if os.path.exists(prop['value']):
            return repr(prop['value'])

        else:
            return repr("icon:" + prop['value'])

    def stat_value(self, prop):
        # TODO: it would be better if icons would be checked in a step between parsing and compiling
        if not prop['value'] in self.icons:
            if not '.' in prop['value']:
                # assume maki icon
                # TODO: check if icon is part of Maki
                pass
            elif os.path.exists(prop['value']):
                img = Image(filename=prop['value'])
                self.icons[prop['value']] = img.size
            else:
                print('Warning: icon {value} not found - can\'t determine size.'.format(**prop))
                self.icons[prop['value']] = None

        return default.stat_value(self, prop)

    def get_global_data(self):
        return self.icons
