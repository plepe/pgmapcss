import pgmapcss.db as db
from .compile_eval import compile_eval
from .compile_value import compile_value
from .CompileError import CompileError

def compile_properties(statement, stat, indent=''):
    ret = ''

    for prop in statement['properties']:
        if prop['assignment_type'] == 'P':
            c = compile_value(prop, stat)

            if c == None:
                raise CompileError('Illegal value for property "%s" found: "%s"' % ( prop['key'], prop['value'] ))

            ret += indent + "current['properties'][" + statement['current_pseudo_element'] + ']' +\
                '[' + repr(prop['key']) + '] = ' + c + '\n'

        elif prop['assignment_type'] == 'T':
            c = compile_value(prop, stat)
            ret += indent + "current['tags']" +\
                '[' + repr(prop['key']) + '] = ' + c + '\n'

        elif prop['assignment_type'] == 'U':
            ret += indent + "current['tags'].pop(" + repr(prop['key']) + ')\n'

        elif prop['assignment_type'] == 'C':
            ret += indent + '''yield(( 'combine', ''' + repr(prop['key']) + \
            ', ' + compile_value(prop, stat) + ''', {
    'id': object['id'],
    'tags': current['tags'],
    'geo': current['properties'][''' + statement['current_pseudo_element'] + ''']['geo']
}))
'''

    return ret
