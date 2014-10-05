from pkg_resources import *

def get_base_style(base_style):
    c = resource_string(__name__, base_style + '.mapcss')
    c = c.decode('utf-8')
    return c
