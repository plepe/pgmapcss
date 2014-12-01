from .compile_selector_part import compile_selector_part
from .compile_conditions import compile_conditions
from .compile_eval import compile_eval
import pgmapcss.db as db

def compile_link_selector(statement, stat):
    parent_conditions = stat['database'].merge_conditions([(
        statement['parent_selector']['type'],
        stat['database'].compile_selector(
            statement, stat, prefix='', selector='parent_selector')
    )])[statement['parent_selector']['type']]

    child_conditions = stat['database'].merge_conditions([(
        statement['selector']['type'],
        stat['database'].compile_selector(
            statement, stat, prefix='')
    )])[statement['selector']['type']]

    if statement['link_selector']['type'] in ('>', ''):
        return "{ 'type': 'objects_member_of', " +\
               "'parent_type': " + repr(statement['parent_selector']['type']) + ", " +\
               "'parent_conditions': " + repr(parent_conditions) + ", " +\
               "'child_conditions': " + repr(child_conditions) + "}"

    elif statement['link_selector']['type'] == '<':
        return "{ 'type': 'objects_members', " +\
               "'parent_type': " + repr(statement['parent_selector']['type']) + ", " +\
               "'parent_conditions': " + repr(parent_conditions) + ", " +\
               "'child_conditions': " + repr(child_conditions) + "}"

    elif statement['link_selector']['type'] == 'near':
        distance = { 'value': '100' }

        for r in statement['link_selector']['conditions']:
            if r['key'] == 'distance' and r['op'] in ('<', '<=', '='):
                distance = r

        if distance.get('value_type') == 'eval':
            distance = compile_eval(distance['value'], {
                    'statement': statement ,
                    'id': statement['id']
                }, stat)
        else:
            distance = repr(distance['value'])

        return "{ 'type': 'objects_near', " +\
               "'parent_type': " + repr(statement['parent_selector']['type']) + ", " +\
               "'parent_conditions': " + repr(parent_conditions) + ", " +\
               "'child_conditions': " + repr(child_conditions) + ", " +\
               "'distance': " + distance + "}"

    elif statement['link_selector']['type'] in ('within', 'surrounds', 'overlaps'):
        return "{ 'type': 'objects_near', " +\
               "'parent_type': " + repr(statement['parent_selector']['type']) + ", " +\
               "'parent_conditions': " + repr(parent_conditions) + ", " +\
               "'child_conditions': " + repr(child_conditions) + ", " +\
               "'distance': " + distance + ", " +\
               "'check_geo': " + repr(statement['link_selector']['type']) + "}"

    else:
        raise Exception('Unknown link selector "{type}"'.format(**selector['link_selector']))
