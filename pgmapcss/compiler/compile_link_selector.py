from .compile_selector_part import compile_selector_part
from .compile_conditions import compile_conditions
import pgmapcss.db as db

def compile_link_selector(statement, stat):
    if statement['link_selector']['type'] in ('>', ''):
        return 'select t_parent_object.* from ' +\
            'objects_' + statement['parent_selector']['type'] +\
            '_member_of(object.id) t_parent_object where ' +\
            compile_selector_part(statement['parent_selector'], stat, 't_parent_object.')

    elif statement['link_selector']['type'] == '<':
        return 'select t_parent_object.* from ' +\
            'objects_' + statement['parent_selector']['type'] +\
            '_members(object.id) t_parent_object where ' +\
            compile_selector_part(statement['parent_selector'], stat, 't_parent_object.')

    elif statement['link_selector']['type'] == 'near':
        distance = 100

        for r in statement['link_selector']['conditions']:
            if r['key'] == 'distance' and r['op'] in ('<', '<='):
                distance = r['value']

        return 'select * from ' +\
            'objects_near(' + db.format(distance) + ', object, current, render_context, ' +\
            db.format({
                statement['parent_selector']['type']: compile_conditions(statement['parent_selector']['conditions'], stat)
            }) + ')'

    else:
        raise Exception('Unknown link selector "{type}"'.format(**selector['link_selector']))
        #return 'select null::text id, null::hstore tags, null::geometry geo, null::text[] types, null::hstore link_tags from generate_series(1, 0)';
