from .default import default
import os
import re

class image(default):
    def __init__(self, key, stat):
        default.__init__(self, key, stat)
        self.icons = {}

    def compile(self, prop):
        if not os.path.exists(prop['value']):
            print("Image '{}' not found.".format(prop['value']))

        return repr(prop['value'])
