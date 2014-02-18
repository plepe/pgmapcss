from .default import default
from .tag_value import tag_value
from .color import color
from .icon import icon

global classes
classes = {
    'default': default,
    'tag_value': tag_value,
    'icon': icon,
    'color': color,
}

properties = {
}

def get(key, stat):
    if key in properties:
        return properties[key]

    t = 'default'
    if 'type' in stat['defines']:
        t = stat['defines']['type'].get(key, { 'value': 'default' })['value']

    if not t in classes:
        print("Warning! Property type {} not defined.".format(t))
        t = 'default'

    properties[key] = classes[t](key, stat)

    return properties[key]
