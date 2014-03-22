from .to_color import to_color
from .color_values import color_values
from .color_names import color_names
from ..includes import register_includes
from pkg_resources import *

register_includes({
    'to_color': resource_string(__name__, 'to_color.py').decode('utf-8'),
    'color_values': resource_string(__name__, 'color_values.py').decode('utf-8'),
    'color_names': resource_string(__name__, 'color_names.py').decode('utf-8')
})
