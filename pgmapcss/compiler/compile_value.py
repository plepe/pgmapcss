import pgmapcss.db as db
import pgmapcss.types
from .compile_eval import compile_eval
import os

def compile_value(prop, stat):
    """returns two values, first a static value which can be put into the 'to_set' dictts, or False if the value is dynamic. The second value is the compiled version."""
    if prop['assignment_type'] == 'P':
        prop_type = pgmapcss.types.get(prop['key'], stat)
    else:
        prop_type = pgmapcss.types.default(None, stat);

    if prop['value_type'] == 'eval':
        return prop_type.compile_check(compile_eval(prop['value'], prop, stat))

    elif prop['value'] == None:
        return 'None'

    else:
        return prop_type.compile(prop)
