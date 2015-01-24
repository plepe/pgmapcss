import pgmapcss.db as db
from .compile_eval import compile_eval
from .compile_value import compile_value
from .compile_requirements import compile_requirements
from .CompileError import CompileError

def compile_properties(statement, stat, indent=''):
    ret = ''

    for prop in statement['properties']:
        if prop['assignment_type'] == 'P':
            res = compile_value(prop, stat)

            if res == None:
                raise CompileError('Illegal value for property "%s" found: "%s"' % ( prop['key'], prop['value'] ))

            ret += indent + "current['properties'][" + statement['current_pseudo_element'] + ']' +\
                '[' + repr(prop['key']) + '] = ' + res['code'] + '\n'

        elif prop['assignment_type'] == 'T':
            res = compile_value(prop, stat)
            ret += indent

            # JOSM classes ("set foo" => set ".foo" too)
            if stat['config'].get('josm_classes', '') == 'true' \
              and prop['key'][0] != '.':
                ret += "current['tags']" +\
                    '[' + repr('.' + prop['key']) + '] = '

            ret += "current['tags']" +\
                '[' + repr(prop['key']) + '] = ' + res['code'] + '\n'

        elif prop['assignment_type'] == 'U':
            # JOSM classes ("set foo" => set ".foo" too)
            if stat['config'].get('josm_classes', '') == 'true' \
              and prop['key'][0] != '.':
                ret += indent + "current['tags'].pop(" + repr('.' + prop['key']) + ', None)\n'

            ret += indent + "current['tags'].pop(" + repr(prop['key']) + ', None)\n'

        elif prop['assignment_type'] == 'C':
            res = compile_value(prop, stat)
            ret += indent + '''yield(( 'combine', ''' + repr(prop['key']) + \
            ', ' + res['code'] + ''', {
    'id': object['id'],
    'tags': current['tags'],
    'geo': current['properties'][''' + statement['current_pseudo_element'] + ''']['geo'] if 'geo' in current['properties'][''' + statement['current_pseudo_element'] + '''] else current['object']['geo']
}))
'''

        if 'options' in res:
            ret = compile_requirements(res['options'], prop, stat, indent) + ret

    return ret
