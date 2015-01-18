from .compile_selector_part import compile_selector_part
from .compile_link_selector import compile_link_selector
from .compile_properties import compile_properties
from .compile_conditions import compile_conditions
from .compile_media_query import compile_media_query
from .compile_eval import *

def and_join(lst):
    if len(lst) == 0:
        return 'True'

    return ' and '.join(lst)

def list_eval_functions(statement, stat):
    ret = set()

    for prop in statement['properties']:
        if prop['value_type'] == 'eval':
            ret = ret.union(eval_uses_functions(prop['value'], stat))

    return ret

def uses_variables(statement, stat):
    variables = set()

    for prop in statement['properties']:
        if prop['assignment_type'] == 'V':
            variables.add(prop['key'])

        if 'value_type' in prop and prop['value_type'] == 'eval':
            l = eval_uses_variables(prop['value'], stat)
            variables = variables.union(l)

    if len(variables) == 0:
        return False

    return variables

def selector_check_variables(selector, stat):
    ret = set()

    for condition in selector['conditions']:
        if condition['op'] == 'eval':
            ret = ret.union(eval_uses_variables(condition['key'], stat))

        elif 'value_type' in condition and condition['value_type'] == 'eval':
            ret = ret.union(eval_uses_variables(condition['value'], stat))

    if 'parent' in selector:
        ret = ret.union(selector_check_variables(selector['parent'], stat))
        ret = ret.union(selector_check_variables(selector['link'], stat))


    return ret

def compile_statement_pending(statement, stat, indent=''):
    ret = ''
    variables = set()

    variables = variables.union(selector_check_variables(statement['selector'], stat))
    variables = variables.union(uses_variables(statement, stat))

    last_assign = {
        k: [
            p
            for p in stat['variables'][k]
            if p <= statement['id']
        ]
        for k in variables
    }

    last_assign = {
        k: v[-1]
        for k, v in last_assign.items()
        if len(v)
    }

    if len(last_assign):
        ret += indent + 'if ' + ' or '.join([
            "global_data['variables-status'][" + repr(k) + "]['done'] < " + str(v)
            for k, v in last_assign.items()
        ]) + ':\n'
        indent += '    '

        ret += indent + 'yield ("pending", ' + str(statement['id']) + ')\n'

    return ret

# returns
# {
#   'check': Check as list, e.g. ['highway=foo', '...'],
#   'body': tags['foo'] = 'bar'
# }
def compile_statement(statement, stat, indent=''):
    ret = { 'check': [], 'body': '', 'pre-check': '' }
    object_selector = statement['selector']
    pending = False

    if 'media' in statement:
        v = compile_media_query(statement['media'], stat)
        if v:
            ret['check'].append(v)

    # check if the selector uses variables
    if not pending and selector_check_variables(object_selector, stat):
        ret['pre-check'] += compile_statement_pending(statement, stat, indent=indent)
        pending = True

    ret['check'] += compile_selector_part(object_selector, stat)

    # for tr() function -> replace {0.tag} and similar
    # TODO: include only in body, when tr() is being used
    if 'f:tr' in list_eval_functions(statement, stat):
        ret['body'] += indent + "current['condition-keys'] = " + repr([
                c['key'] if 'key' in c else None
                for c in object_selector['conditions']
            ]) + '\n'

    if not pending and uses_variables(statement, stat):
        ret['body'] += compile_statement_pending(statement, stat, indent=indent)
        pending = True

    if 'link' in statement['selector']:
        ret['body'] += indent + '# link selector -> get list of objects, but return with "request", so that statements of parent objects up to the current statement can be processed. Remember link tags, add them later-on.\n'
        ret['body'] += indent + 'objects = yield ("request", ' + str(statement['id']) + ', ' + compile_link_selector(statement, stat) + ')\n'
        ret['body'] += indent + 'for parent_index, (parent_object, link_tags) in enumerate(objects):\n'

        indent += '    '
        ret['body'] += indent + "current['parent_object'] = parent_object\n"
        ret['body'] += indent + "current['link_object'] = { 'tags': link_tags }\n"
        ret['body'] += indent + "current['link_object']['tags']['index'] = str(parent_index)\n"
        ret['body'] += indent + 'if (' +\
          and_join(compile_conditions(statement['selector']['parent']['conditions'], stat, "current['parent_object']['tags']")) +\
          ') and (' +\
          and_join(compile_conditions(statement['selector']['link']['conditions'], stat, "current['link_object']['tags']")) + '):\n'

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

    if 'link' in statement['selector']:
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
