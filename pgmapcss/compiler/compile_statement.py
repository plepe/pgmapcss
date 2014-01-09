from .compile_selector_part import compile_selector_part
from .compile_link_selector import compile_link_selector
from .compile_properties import compile_properties
from .compile_conditions import compile_conditions

def compile_statement(statement, stat):
    ret = ''
    object_selector = statement['selector']

    ret += 'if (' + compile_selector_part(object_selector, stat) + ')\nthen\n'

    if 'link_selector' in statement:
        ret += 'parent_index := 0;\n'
        ret += 'for parent_object in ' + compile_link_selector(statement, stat) + ' loop\n'
        ret += 'parent_index := parent_index + 1;\n'
        ret += 'o.tags := parent_object.link_tags || hstore(\'index\', cast(parent_index as text));\n'
        ret += 'if (' + compile_conditions(statement['link_selector']['conditions'], stat, 'o.') + ') then\n'
        ret += 'current.parent_object = parent_object;\n'
        ret += 'current.link_object = o;\n'

    # set current.pseudo_element_ind
    if object_selector['pseudo_element'] == '*':
        statement['current_pseudo_element'] = 'i'
        ret += 'for i in 1..array_upper(current.pseudo_elements, 1) loop\n'
    else:
        statement['current_pseudo_element'] = str(stat['pseudo_elements'].index(object_selector['pseudo_element']) + 1)
    ret += 'current.pseudo_element_ind = ' + statement['current_pseudo_element'] + ';\n'

# TODO: prop_type
    ret += compile_properties(statement, stat)

    if object_selector['pseudo_element'] == '*':
        ret += 'end loop;\n'

    if 'link_selector' in statement:
        ret += 'end if;\n'
        ret += 'end loop;\n'
        ret += 'current.parent_object = null;\n'

# create_pseudo_element
    if not 'create_pseudo_element' in object_selector or \
        object_selector['create_pseudo_element']:
        ret += 'current.has_pseudo_element[' + statement['current_pseudo_element'] + '] = true;\n'

    ret += 'end if;\n\n'

    return ret
