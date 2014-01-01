from .compile_selector_part import compile_selector_part
from .compile_properties import compile_properties

def compile_statement(statement, stat):
    ret = ''
    object_selector = statement['selectors']

    ret += 'if (' + compile_selector_part(object_selector, stat) + ')\nthen\n'
# TODO: link

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

# create_pseudo_element
    if not 'create_pseudo_element' in object_selector or \
        object_selector['create_pseudo_element']:
        ret += 'current.has_pseudo_element[' + statement['current_pseudo_element'] + '] = true;\n'

    ret += 'end if;\n\n'

    return ret
