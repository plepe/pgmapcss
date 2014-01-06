import pg
from .compile_eval import compile_eval

def compile_value(prop, stat):
    if prop['value_type'] == 'eval':
        return compile_eval(prop['value'])

    else:
        return pg.format(prop['value'])


def compile_properties(statement, stat):
    ret = ''
    to_set = { 'prop': {}, 'tags': {} }

    for prop in statement['properties']:
        if prop['assignment_type'] == 'P':
            if prop['value_type'] == 'eval':
                ret += print_props_and_tags(statement['current_pseudo_element'], to_set)
                ret += 'current.styles[' + statement['current_pseudo_element'] + '] = ' +\
                    'current.styles[' + statement['current_pseudo_element'] + '] || ' +\
                    'hstore(' + pg.format(prop['key']) + ', ' +\
                    compile_eval(prop['value']) + ');\n'

            else:
                if prop['value_type'] == 'value' and \
                    'type' in stat['defines'] and \
                    prop['key'] in stat['defines']['type']:

                    ret += print_props_and_tags(statement['current_pseudo_element'], to_set)
                    ret += 'current.styles[' + statement['current_pseudo_element'] + '] = ' +\
                        'current.styles[' + statement['current_pseudo_element'] + '] || ' +\
                        'hstore(' + pg.format(prop['key']) + ', (current.tags)-> ' +\
                        pg.format(prop['value']) + ');\n'

                else:
                    to_set['prop'][prop['key']] = prop['value']

        elif prop['assignment_type'] == 'T':
            if prop['value_type'] == 'eval':
                ret += print_props_and_tags(statement['current_pseudo_element'], to_set)
                ret += 'current.tags = ' +\
                    'current.tags || ' +\
                    'hstore(' + pg.format(prop['key']) + ', ' +\
                    compile_eval(prop['value']) + ');\n'

            else:
                to_set['tags'][prop['key']] = prop['value']

        elif prop['assignment_type'] == 'C':
            ret += print_props_and_tags(statement['current_pseudo_element'], to_set)
            ret += 'return query select object.id, current.tags, current.styles[' + statement['current_pseudo_element'] + ']->\'geo\', object.types, null::text, null::hstore, null::text, ' + pg.format(prop['key']) + '::text, ' + compile_value(prop, stat) + ';\n';

    ret += print_props_and_tags(statement['current_pseudo_element'], to_set)

    return ret

def print_props_and_tags(current_pseudo_element, to_set):
  ret = ''

  if len(to_set['prop']):
      ret += 'current.styles[' + current_pseudo_element + '] = ' +\
          'current.styles[' + current_pseudo_element + '] || ' +\
          pg.format(to_set['prop']) + ';\n'
      to_set['prop'].clear()

  if len(to_set['tags']):
      ret += 'current.tags = current.tags || ' +\
          pg.format(to_set['tags']) + ';\n'
      to_set['tags'].clear()

  return ret
