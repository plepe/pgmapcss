from .compile_selector_part import compile_selector_part
import pghstore

def print_props_and_tags(current_pseudo_element, prop_to_set, tags_to_set):
  ret = ''

  if len(prop_to_set):
      ret += 'current.styles[' + current_pseudo_element + '] = ' +\
          'current.styles[' + current_pseudo_element + '] || \'' +\
          pghstore.dumps(prop_to_set) + '\';\n'
      prop_to_set.clear()

  if len(tags_to_set):
      ret += 'current.tags = current.tags || \'' +\
          pghstore.dumps(tags_to_set) + '\';\n'
      tags_to_set.clear()

  return ret

def compile_statement(statement, stat):
    ret = ''
    object_selector = statement['selectors']

    ret += 'if (' + compile_selector_part(object_selector, stat) + ')\nthen\n'
# TODO: link

    # set current.pseudo_element_ind
    if object_selector['pseudo_element'] == '*':
        current_pseudo_element = 'i'
        ret += 'for i in 1..array_upper(current.pseudo_elements, 1) loop\n'
    else:
        current_pseudo_element = str(stat['pseudo_elements'].index(object_selector['pseudo_element']))
    ret += 'current.pseudo_element_ind = ' + current_pseudo_element + ';\n'

    prop_to_set = {}
    tags_to_set = {}

# TODO: prop_type
    for prop in statement['properties']:
        if prop['assignment_type'] == 'P':
            if prop['value_type'] == 0:
                prop_to_set[prop['key']] = prop['value']

        elif prop['assignment_type'] == 'T':
            if prop['value_type'] == 0:
                tags_to_set[prop['key']] = prop['value']

    ret += print_props_and_tags(current_pseudo_element, prop_to_set, tags_to_set)

    if object_selector['pseudo_element'] == '*':
        ret += 'end loop;\n'

# create_pseudo_element
    if not 'create_pseudo_element' in object_selector or \
        object_selector['create_pseudo_element']:
        ret += 'current.has_pseudo_element[' + current_pseudo_element + '] = true;\n'

    ret += 'end if;\n\n'

    return ret
