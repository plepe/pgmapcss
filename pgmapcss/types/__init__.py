from .default import default
from .tag_value import tag_value
from .color import color
from .icon import icon
from .image import image
from .image_png import image_png
from .values import values
from .pixels import pixels
from .numeric import numeric
from .dashes import dashes
from .angle import angle
from .list_append import list_append

global classes
classes = {
    'default': default,
    'tag_value': tag_value,
    'icon': icon,
    'image': image,
    'image_png': image_png,
    'color': color,
    'values': values,
    'pixels': pixels,
    'numeric': numeric,
    'dashes': dashes,
    'angle': angle,
    'list_append': list_append,
}

properties = {
}

def get(key, stat):
    if key in properties:
        return properties[key]

    t = 'default'
    if 'type' in stat['defines']:
        t = stat['defines']['type'].get(key, { 'value': 'default' })['value']

    if 'values' in stat['defines'] and key in stat['defines']['values']:
        t = 'values'

    if not t in classes:
        print("Warning! Property type {} not defined.".format(t))
        t = 'default'

    properties[key] = classes[t](key, stat)

    return properties[key]
