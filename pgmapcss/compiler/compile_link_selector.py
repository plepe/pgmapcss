from .compile_selector_part import compile_selector_part
from .compile_conditions import compile_conditions
from .compile_eval import compile_eval
import pgmapcss.db as db

def compile_link_selector(statement, stat):
    # create statement where selector is build from parent_selector for compiling
    parent_conditions = stat['database'].merge_conditions([(
        statement['selector']['parent']['type'],
        stat['database'].compile_selector(statement['selector']['parent'])
    )])

    if statement['selector']['parent']['type'] in parent_conditions:
        parent_conditions = parent_conditions[statement['selector']['parent']['type']]
    else:
        parent_conditions = None

    child_conditions = stat['database'].merge_conditions([(
        statement['selector']['type'],
        stat['database'].compile_selector(statement['selector'])
    )])
    if statement['selector']['type'] in child_conditions:
        child_conditions = child_conditions[statement['selector']['type']]
    else:
        child_conditions = None

    if statement['selector']['link']['type'] in ('>', ''):
        return "objects_member_of(object['id'], " +\
            repr(statement['selector']['parent']['type']) + ", " +\
            repr(parent_conditions) + ", " +\
            repr(child_conditions) + ")"

    elif statement['selector']['link']['type'] == '<':
        return "objects_members(object['id'], " +\
            repr(statement['selector']['parent']['type']) + ", " +\
            repr(parent_conditions) + ", " +\
            repr(child_conditions) + ")"

    elif statement['selector']['link']['type'] == 'near':
        distance = { 'value': '100' }

        for r in statement['selector']['link']['conditions']:
            if r['key'] == 'distance' and r['op'] in ('<', '<=', '='):
                distance = r

        if distance.get('value_type') == 'eval':
            distance = compile_eval(distance['value'], {
                    'statement': statement ,
                    'id': statement['id']
                }, stat)
        else:
            distance = repr(distance['value'])

        return "objects_near(" + distance + ", None, "+\
            repr(statement['selector']['parent']['type']) + ", " +\
            repr(parent_conditions) + ", " +\
            repr(child_conditions) + ")"

    elif statement['selector']['link']['type'] in ('within', 'surrounds', 'overlaps'):
        return "objects_near(\"0\", None, "+\
            repr(statement['selector']['parent']['type']) + ", " +\
            repr(parent_conditions) + ", " +\
            repr(child_conditions) + ", check_geo=" +\
            repr(statement['selector']['link']['type']) + ")"

    else:
        raise Exception('Unknown link selector "{type}"'.format(**selector['selector']['link']))
