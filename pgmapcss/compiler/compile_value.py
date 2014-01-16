import pgmapcss.db as db
from .compile_eval import compile_eval

def compile_value(prop, stat):
    """returns two values, first a static value which can be put into the 'to_set' dictts, or False if the value is dynamic. The second value is the compiled version."""
    if prop['value_type'] == 'eval':
        return compile_eval(prop['value'])

    elif 'unit' in prop and prop['unit'] in ('m', 'u'):
        return compile_eval([ 'f:metric', 'v:' + prop['value'] + prop['unit'] ])

    elif prop['value'] == None:
        return 'None'

    elif prop['value_type'] == 'value' and \
        prop['assignment_type'] == 'P' and \
        'type' in stat['defines'] and \
        prop['key'] in stat['defines']['type'] and \
        stat['defines']['type'][prop['key']]['value'] == "tag_value":
        return "current['tags'][" + repr(prop['value']) +']'

    else:
        return repr(prop['value'])
