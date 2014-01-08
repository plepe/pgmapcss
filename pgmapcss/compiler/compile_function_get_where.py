import pgmapcss.db as db
from .stat import *
from .compile_condition import compile_condition

def get_where_selectors(max_scale, min_scale, stat):
    # where_selectors contains indexes of all selectors which we need for match queries
    where_selectors = []

    # get list of properties which are 'important' (create a symbol)
    style_element_properties = [
        k
        for i, j in stat['defines']['style_element_property'].items()
        for k in j['value'].split(';')
    ]

    # where_selectors: find list of selectors which are relevent for db where
    # matches (all that have an entry in @style_element_property)
    where_selectors += [
        i
        for i, v in enumerate(stat['statements'])
        for w in v['properties']
        if ((w['key'] in style_element_properties and w['assignment_type'] == 'P') or
            w['assignment_type'] == 'C') and
            v['selector']['min_scale'] <= min_scale and
            (v['selector']['max_scale'] == None or v['selector']['max_scale'] >= max_scale) and
            not 'create_pseudo_element' in v['selector']
    ]

    # TODO combine

    # list of all tag assignments in form ( 'key', 'value', index of statement )
    # if value results of an eval statement use True instead
    list_tag_assignments = [
        (
            p['key'],
            True if p['value_type'] == 'eval' else p['value'],
            i 
        )
        for i, v in enumerate(stat['statements'])
        for p in v['properties'] if p['assignment_type'] == 'T'
        if v['selector']['min_scale'] <= min_scale and
            (v['selector']['max_scale'] == None or v['selector']['max_scale'] >= max_scale)
    ]

    # assignments: map conditions which are based on a (possible) set-statement
    # back to their original selectors:
    where_selectors += [
        j[2]
        for j in list_tag_assignments
        for i, v in enumerate(stat['statements'])
        for s in v['selector']['conditions']
        for w in v['properties']
        if ((w['key'] in style_element_properties and
            w['assignment_type'] == 'P') or
            w['assignment_type'] == 'C') and
            j[2] < i and s['key'] == j[0] and
            (j[1] == True or not 'value' in s or s['value'] == j[1]) and
            v['selector']['min_scale'] <= min_scale and
            (v['selector']['max_scale'] == None or v['selector']['max_scale'] >= max_scale) and
            not 'create_pseudo_element' in v['selector']
    ]

    # uniq list
    return list(set(where_selectors))

def compile_function_get_where(id, stat):
    ret = ''

    scale_denominators = stat_all_scale_denominators(stat)

    max_scale = None
    for min_scale in scale_denominators:
        where_selectors = get_where_selectors(max_scale or 10E+10, min_scale, stat)

        # compile all selectors
        conditions = [
            (
                stat['statements'][i]['selector']['type'],
                ' and '.join(
                    [ 'true' ] +
                    [
                        compile_condition(c, stat, prefix='', match_where=True) or 'true'
                        for c in stat['statements'][i]['selector']['conditions']
                    ]
                )
            )
            for i in where_selectors
        ]

        # Move all conditions with * as type selector to all other types
        all_types_conditions = []
        for c in conditions:
            if c[0] == True:
                all_types_conditions.append(c[1])

        types = [ t for t, cs in conditions if t != True ]

        conditions = {
            t:
                '(' + ') or ('.join([
                    cs
                    for t2, cs in conditions
                    if t == t2
                ] + all_types_conditions ) + ')'
            for t in types
        }

        max_scale = min_scale

        if ret == '':
            ret += '  if'
        else:
            ret += '  elsif'

        ret += \
            ' render_context.scale_denominator >= ' + str(min_scale) + ' then\n' +\
            '    return ' + db.format(conditions) + ';\n'

    ret += '  end if;\n\n'

    replacement = {
      'style_id': id,
      'content': ret
    }

    ret = '''\
create or replace function {style_id}_get_where(
  render_context\tpgmapcss_render_context
) returns hstore as $body$
declare
begin
{content}
end;
$body$ language 'plpgsql' immutable;
'''.format(**replacement)

    return ret
