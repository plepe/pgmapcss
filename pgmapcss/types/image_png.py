from .default import default
import os
import re
from wand.image import Image

class image_png(default):
    def __init__(self, key, stat):
        default.__init__(self, key, stat)
        self.icons = {}

    def compile(self, prop):
        if not os.path.exists(prop['value']):
            print("Image '{}' not found.".format(prop['value']))
            return repr(prop['value'])

        else:
            # Convert SVG to PNG
            m = re.match("([^\/]*)\.svg", prop['value'])
            if m:
                dest = self.stat['icons_dir'] + "/" + m.group(1) + ".png"
                print("svg icon detected. converting '{0}' to '{1}'".format(prop['value'], dest))

                with Image(filename=prop['value']) as img:
                    img.format = 'png'
                    img.save(filename=dest)

                return repr(dest)

            return repr(prop['value'])
