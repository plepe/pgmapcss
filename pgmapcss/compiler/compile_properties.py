import pgmapcss.db as db
from .compile_eval import compile_eval
from .compile_value import compile_value

def compile_properties(statement, stat, indent=''):
    ret = ''

    for prop in statement['properties']:
        if prop['assignment_type'] == 'P':
            c = compile_value(prop, stat)
            ret += indent + "current['properties'][" + statement['current_pseudo_element'] + ']' +\
                '[' + repr(prop['key']) + '] = ' + c + '\n'

        elif prop['assignment_type'] == 'T':
            c = compile_value(prop, stat)
            ret += indent + "current['tags']" +\
                '[' + repr(prop['key']) + '] = ' + c + '\n'

        elif prop['assignment_type'] == 'U':
            ret += indent + "current['tags'].pop(" + repr(prop['key']) + '\n'

        elif prop['assignment_type'] == 'C':
            ret += indent + '''yield({
    'id': object['id'],
    'tags': pghstore.dumps(current['tags']),
    'geo': current['properties'][''' + statement['current_pseudo_element'] + ''']['geo'],
    'types': object['types'],
    'pseudo_element': None,
    'properties': None,
    'style-element': None,
    'combine_type': ''' + repr(prop['key']) + ''',
    'combine_id': ''' + compile_value(prop, stat) + ''',
})
'''

    return ret
