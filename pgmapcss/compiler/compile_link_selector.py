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
        return "{ 'type': 'objects_member_of', " +\
                "'other_selects': " + repr(other_selects) + ", " +\
                "'self_selects': " + repr(self_selects) + ", " +\
                "'options': {} }"

    elif statement['selector']['link']['type'] == '<':
        return "{ 'type': 'objects_members', " +\
                "'other_selects': " + repr(other_selects) + ", " +\
                "'self_selects': " + repr(self_selects) + ", " +\
                "'options': {} }"

    elif statement['selector']['link']['type'] == 'near':
        distance = { 'value': '100' }

        for r in statement['selector']['link']['conditions']:
            if r['key'] == 'distance' and r['op'] in ('<', '<=', '='):
                distance = r

        if distance.get('value_type') == 'eval':
            result = compile_eval(distance['value'], {
                    'statement': statement ,
                    'id': statement['id']
                }, stat)
            distance = result['code']
        else:
            distance = repr(distance['value'])

        return "{ 'type': 'objects_near', " +\
               "'other_selects': " + repr(other_selects) + ", " +\
               "'self_selects': " + repr(self_selects) + ", " +\
               "'options': { " +\
               "'distance': " + distance +\
               "}}"

    elif statement['link_selector']['type'] in ('within', 'surrounds', 'overlaps'):
        return "{ 'type': 'objects_near', " +\
               "'other_selects': " + repr(other_selects) + ", " +\
               "'self_selects': " + repr(self_selects) + ", " +\
               "'options': { " +\
               "'distance': 0," +\
               "'check_geo': " + repr(statement['link_selector']['type']) +\
               " }}"

    else:
        raise Exception('Unknown link selector "{type}"'.format(**selector['selector']['link']))
