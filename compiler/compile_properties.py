import pg
from .compile_eval import compile_eval

def compile_properties(statement, stat):
    ret = ''
    to_set = { 'prop': {}, 'tags': {} }

    for prop in statement['properties']:
        if not prop['key'] in stat['properties_values']:
            stat['properties_values'][prop['key']] = set()

        if prop['assignment_type'] == 'P':
            if prop['value_type'] == 'eval':
                ret += print_props_and_tags(statement['current_pseudo_element'], to_set)
                ret += 'current.styles[' + statement['current_pseudo_element'] + '] = ' +\
                    'current.styles[' + statement['current_pseudo_element'] + '] || ' +\
                    'hstore(' + pg.format(prop['key']) + ', ' +\
                    compile_eval(prop['value']) + ');\n'

                stat['properties_values'][prop['key']].add(True)

            else:
                if prop['value_type'] == 'value' and \
                    'type' in stat['defines'] and \
                    prop['key'] in stat['defines']['type']:

                    ret += print_props_and_tags(statement['current_pseudo_element'], to_set)
                    ret += 'current.styles[' + statement['current_pseudo_element'] + '] = ' +\
                        'current.styles[' + statement['current_pseudo_element'] + '] || ' +\
                        'hstore(' + pg.format(prop['key']) + ', (current.tags)-> ' +\
                        pg.format(prop['value']) + ');\n'

                    stat['properties_values'][prop['key']].add(True)

                else:
                    to_set['prop'][prop['key']] = prop['value']

                    stat['properties_values'][prop['key']].add(prop['value'])

        elif prop['assignment_type'] == 'T':
            if prop['value_type'] == 'eval':
                ret += print_props_and_tags(statement['current_pseudo_element'], to_set)
                ret += 'current.tags = ' +\
                    'current.tags || ' +\
                    'hstore(' + pg.format(prop['key']) + ', ' +\
                    compile_eval(prop['value']) + ');\n'

            else:
                to_set['tags'][prop['key']] = prop['value']

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