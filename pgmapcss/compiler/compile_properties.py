import pgmapcss.db as db
from .compile_eval import compile_eval
from .compile_value import compile_value

def compile_properties(statement, stat):
    ret = ''
    to_set = { 'prop': {}, 'tags': {} }

    for prop in statement['properties']:
        if prop['assignment_type'] == 'P':
            c = compile_value(prop, stat)
            if c[0] != False:
                to_set['prop'][prop['key']] = c[0]
            else:
                ret += print_props_and_tags(statement['current_pseudo_element'], to_set)
                ret += 'current.styles[' + statement['current_pseudo_element'] + '] = ' +\
                    'current.styles[' + statement['current_pseudo_element'] + '] || ' +\
                    'hstore(' + db.format(prop['key']) + ', ' +\
                    c[1] + ');\n'

        elif prop['assignment_type'] == 'T':
            c = compile_value(prop, stat)
            if c[0] != False:
                to_set['tags'][prop['key']] = prop['value']
            else:
                ret += print_props_and_tags(statement['current_pseudo_element'], to_set)
                ret += 'current.tags = ' +\
                    'current.tags || ' +\
                    'hstore(' + db.format(prop['key']) + ', ' +\
                    c[1] + ');\n'

        elif prop['assignment_type'] == 'U':
            ret += print_props_and_tags(statement['current_pseudo_element'], to_set)
            ret += 'current.tags = ' +\
                'current.tags - ' + db.format(prop['key']) + '::text;\n'

        elif prop['assignment_type'] == 'C':
            ret += print_props_and_tags(statement['current_pseudo_element'], to_set)
            ret += 'return query select object.id, current.tags, current.styles[' + statement['current_pseudo_element'] + ']->\'geo\', object.types, null::text, null::hstore, null::text, ' + db.format(prop['key']) + '::text, ' + compile_value(prop, stat)[1] + ';\n';

    ret += print_props_and_tags(statement['current_pseudo_element'], to_set)

    return ret

def print_props_and_tags(current_pseudo_element, to_set):
  ret = ''

  if len(to_set['prop']):
      ret += 'current.styles[' + current_pseudo_element + '] = ' +\
          'current.styles[' + current_pseudo_element + '] || ' +\
          db.format(to_set['prop']) + ';\n'
      to_set['prop'].clear()

  if len(to_set['tags']):
      ret += 'current.tags = current.tags || ' +\
          db.format(to_set['tags']) + ';\n'
      to_set['tags'].clear()

  return ret
