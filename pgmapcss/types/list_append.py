from .default import default
from ..includes import register_includes

class list_append(default):
    def __init__(self, key, stat):
        default.__init__(self, key, stat)
        register_includes({
            'list_append': '''
def list_append(key, value):
    if not key in current['properties'][current['pseudo_element']]:
        return value
    else:
        return current['properties'][current['pseudo_element']][key] + ";" + value
'''
        })

    def compile_check(self, value):
        return "list_append(" + repr(self.key) + ", " + value +")"

    def compile(self, prop):
        return "list_append(" + repr(self.key) + ", " + repr(prop['value']) + ")"
