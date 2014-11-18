from .strip_includes import strip_includes
from .pgcache import PGCache
from .pgcache import get_PGCache

from ..includes import register_includes
from pkg_resources import *
register_includes({
    'pgcache': resource_string(__name__, 'pgcache.py').decode('utf-8'),
})
