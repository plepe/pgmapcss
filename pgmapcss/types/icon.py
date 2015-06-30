from .default import default
import os

class icon(default):
    def __init__(self, key, stat):
        default.__init__(self, key, stat)
        self.data = {}

    def compile(self, prop):
        if prop['value'] is None:
            return prop['value']

        return repr(prop['value'])

    def stat_value(self, prop):
        # TODO: it would be better if icons would be checked in a step between parsing and compiling
        if not prop['value'] in self.data:
            if not '.' in prop['value']:
                # assume maki icon
                # TODO: check if icon is part of Maki
                pass
            elif os.path.exists(self.stat['dir_name'] + '/' + prop['value']):
                from wand.image import Image
                img = Image(filename=self.stat['dir_name'] + '/' + prop['value'])
                self.data[prop['value']] = img.size
            else:
                print('Warning: icon {value} not found - can\'t determine size.'.format(**prop))
                self.data[prop['value']] = None

        return default.stat_value(self, prop)

    def get_global_data(self):
        self.stat.property_values(self.key)
        return self.data
