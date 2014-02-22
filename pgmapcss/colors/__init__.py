from .to_color import to_color
from .color_values import color_values
from pkg_resources import *

def includes():
    return {
        'to_color': resource_string(__name__, 'to_color.py').decode('utf-8'),
        'color_values': resource_string(__name__, 'color_values.py').decode('utf-8')
    }
