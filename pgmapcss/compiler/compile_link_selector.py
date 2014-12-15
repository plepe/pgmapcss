from .compile_selector_part import compile_selector_part
from .compile_conditions import compile_conditions
from .compile_db_selects import compile_selectors_db
from .compile_eval import compile_eval
import pgmapcss.db as db

def compile_link_selector(statement, stat):
    # create statement where selector is build from parent_selector for compiling
    other_selects = compile_selectors_db([statement], 'parent', stat)
    self_selects = compile_selectors_db([statement], None, stat)

    if statement['selector']['link']['type'] in ('>', ''):
        return "objects_member_of([object], " +\
            repr(other_selects) + ", " +\
            repr(self_selects) + ", " +\
            repr({}) + ")"

    elif statement['selector']['link']['type'] == '<':
        return "objects_members([object], " +\
            repr(other_selects) + ", " +\
            repr(self_selects) + ", " +\
            repr({}) + ")"

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
            distance = distance['value']

        return "objects_near([object], " +\
            repr(other_selects) + ", " +\
            repr(self_selects) + ", " +\
            repr({
                'distance': distance
            }) + ")"

    elif statement['selector']['link']['type'] in ('within', 'surrounds', 'overlaps'):
        return "objects_near([object], " +\
            repr(other_selects) + ", " +\
            repr(self_selects) + ", " +\
            repr({
                'distance': 0,
                'check_geo': statement['selector']['link']['type'],
            }) + ")"

    else:
        raise Exception('Unknown link selector "{type}"'.format(**selector['selector']['link']))
