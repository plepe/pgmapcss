from .compile_selector_part import compile_selector_part
from .compile_conditions import compile_conditions
from .compile_condition_sql import compile_condition_sql
from .compile_eval import compile_eval
import pgmapcss.db as db

def compile_link_selector(statement, stat):
    parent_conditions = ' and '.join([
        compile_condition_sql(c, stat, prefix='') or 'true'
        for c in statement['parent_selector']['conditions']
    ])

    if statement['link_selector']['type'] in ('>', ''):
        return "objects_member_of(object['id'], " +\
            repr(statement['parent_selector']['type']) + ", " +\
            repr(parent_conditions) + ")"

    elif statement['link_selector']['type'] == '<':
        return "objects_members(object['id'], " +\
            repr(statement['parent_selector']['type']) + ", " +\
            repr(parent_conditions) + ")"

    elif statement['link_selector']['type'] == 'near':
        distance = '100'

        for r in statement['link_selector']['conditions']:
            if r['key'] == 'distance' and r['op'] in ('<', '<='):
                distance = r

        if distance.get('value_type') == 'eval':
            distance = compile_eval(distance['value'])
        else:
            distance = repr(distance['value'])

        return "objects_near(" + distance + ", None, "+\
            repr(statement['parent_selector']['type']) + ", " +\
            repr(parent_conditions) + ")"

    else:
        raise Exception('Unknown link selector "{type}"'.format(**selector['link_selector']))
        #return 'select null::text id, null::hstore tags, null::geometry geo, null::text[] types, null::hstore link_tags from generate_series(1, 0)';
