from .default import default
import os
import re

class image_png(default):
    def __init__(self, key, stat):
        default.__init__(self, key, stat)
        self.data = {}

    def compile(self, prop):
        if not os.path.exists(prop['value']):
            print("Image '{}' not found.".format(prop['value']))

        else:
            # Convert SVG to PNG
            m = re.search("\.svg$", prop['value'])
            if m:
                from wand.image import Image
                from wand.color import Color
                from wand.api import library
                dest = self.stat['icons_dir'] + "/" + prop['value'].replace('/', '_') + ".png"
                print("svg icon detected. converting '{0}' to '{1}'".format(prop['value'], dest))

                with Image() as img:
                    with Color('transparent') as bg_color:
                        library.MagickSetBackgroundColor(img.wand, bg_color.resource)
                    img.read(blob=open(prop['value'], 'rb').read())
                    dest_img = img.make_blob('png32')

                    with open(dest, 'wb') as out:
                        out.write(dest_img)

                return repr(dest)

        return repr(prop['value'])

    def stat_value(self, prop):
        if prop['value'] is None:
            return prop['value']

        if os.path.exists(prop['value']):
            from wand.image import Image
            img = Image(filename=prop['value'])
            self.data[prop['value']] = img.size
            if not prop['key'] in self.stat['global_data']:
                self.stat['global_data'][prop['key']] = {}

            self.stat['global_data'][prop['key']][prop['value']] = img.size

        return prop['value']

    def get_global_data(self):
        self.stat.property_values(self.key)
        return self.data
