from .create_template import create_template
from .init import init
from ..includes import register_includes
from pkg_resources import *

register_includes({
    'load_translation': resource_string(__name__, 'load_translation.py').decode('utf-8'),
})
