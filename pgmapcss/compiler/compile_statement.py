from .compile_selector_part import compile_selector_part
from .compile_link_selector import compile_link_selector
from .compile_properties import compile_properties
from .compile_conditions import compile_conditions
from .compile_media_query import compile_media_query

def and_join(lst):
    if len(lst) == 0:
        return 'True'

    return ' and '.join(lst)

# returns
# {
#   'check': Check as list, e.g. ['highway=foo', '...'],
#   'body': tags['foo'] = 'bar'
# }
def compile_statement(statement, stat, indent=''):
    ret = { 'check': [], 'body': '' }
    object_selector = statement['selector']

    if 'media' in statement:
        v = compile_media_query(statement['media'], stat)
        if v:
            ret['check'].append(v)

    ret['check'] += compile_selector_part(object_selector, stat)

    # for tr() function -> replace {0.tag} and similar
    # TODO: include only in body, when tr() is being used
    ret['body'] += indent + "current['condition-keys'] = " + repr([
            c['key'] if 'key' in c else None
            for c in object_selector['conditions']
        ]) + '\n'

    if 'link_selector' in statement:
        ret['body'] += indent + 'for parent_index, parent_object in enumerate(' + compile_link_selector(statement, stat) + '):\n'

        indent += '    '
        ret['body'] += indent + "current['parent_object'] = parent_object\n"
        ret['body'] += indent + "current['link_object'] = { 'tags': parent_object['link_tags'] }\n"
        ret['body'] += indent + "current['link_object']['tags']['index'] = str(parent_index)\n"
        ret['body'] += indent + 'if (' +\
          and_join(compile_conditions(statement['parent_selector']['conditions'], stat, "current['parent_object']['tags']")) +\
          ') and (' +\
          and_join(compile_conditions(statement['link_selector']['conditions'], stat, "current['link_object']['tags']")) + '):\n'

        indent += '    '
        ret['body'] += indent + 'current[\'parent_object\'] = parent_object\n'

    # set current.pseudo_element_ind
    if object_selector['pseudo_element'] == '*':
        statement['current_pseudo_element'] = 'pseudo_element'
        ret['body'] += indent + "for pseudo_element in current['pseudo_elements']:\n"
        indent += '    '
        ret['body'] += indent + "current['pseudo_element'] = pseudo_element\n"
    else:
        statement['current_pseudo_element'] = repr(object_selector['pseudo_element'])
        ret['body'] += indent + "current['pseudo_element'] = " + statement['current_pseudo_element'] + '\n'

    # Check if a property with 'return_after_statement' appears in the statement
    return_after_statement = True in [
        'return_after_statement' in stat['defines']['property_config'].get(prop['key'], {'value': ''})['value'].split(';')
        for prop in statement['properties']
        if prop['assignment_type'] == 'P'
    ]

    # if a 'return_each_statement' property appears, first save current properties and create a copy (so we don't overwrite current properties)
    if return_after_statement:
        ret['body'] += indent + "prop_save = current['properties']\n"
        ret['body'] += indent + "current['properties'] = copy.deepcopy(prop_save)\n"

# TODO: prop_type
    ret['body'] += compile_properties(statement, stat, indent)

    if object_selector['pseudo_element'] == '*':
        indent = indent[4:]

    if 'link_selector' in statement:
        ret['body'] += indent + "current['parent_object'] = None\n"
        indent = indent[8:]

# create_pseudo_element
    if not 'create_pseudo_element' in object_selector or \
        object_selector['create_pseudo_element']:
        ret['body'] += indent + "current['has_pseudo_element'][" + statement['current_pseudo_element'] + '] = True\n'

    if return_after_statement:
        ret['body'] += indent + "yield ( 'result', build_result(current, current['pseudo_element']) )\n"
        ret['body'] += indent + "current['properties'] = prop_save\n"

    return ret
