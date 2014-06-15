import re
from .parse_string import parse_string
from .parse_eval import parse_eval
from .ParseError import *
from .ParseFile import ParseFile

def parse_url(current, to_parse):
    if to_parse.match('\s*url\('):
        s = parse_string(to_parse)

        if s:
            if to_parse.match('\s*\)\s*'):
                current['value'] = s
                current['value_type'] = 'url'
                return

        else:
            if to_parse.match('([^\)]*)\)'):
                current['value'] = to_parse.match_group(1)
                current['value_type'] = 'url'
                return
    else:
        if to_parse.match('\s*([^;]*)'):
            current['value'] = to_parse.match_group(1)
            current['value_type'] = 'url'
            return to_parse

def parse_value(current, to_parse):
    # strip prepending whitespace
    while True:
        if not to_parse.match('\s+'):
            break;

    # "..." or '...'
    s = parse_string(to_parse)
    if s is not None:
        if to_parse.match('\s*'):
            current['value'] = s
            current['value_type'] = 'string'
            return

    # eval( ... )
    elif to_parse.match('eval\s*\(\s*'):
        fp = to_parse.pos()
        r = parse_string(to_parse)
        value = None

        # if eval statement is of form eval("2 + 3")
        if r != None and to_parse.match('\s*\)\s*', wind=None):
            r = ParseFile(content=r)
            try:
                value = parse_eval(r)
            except ParseError as e:
                to_parse.seek(fp)
                pass

        if value == None:
            to_parse.seek(fp)
            value = parse_eval(to_parse)

        if not to_parse.match('\s*\)\s*'):
            raise ParseError(to_parse, 'Error parsing eval statement')

        current['value'] = value
        current['value_type'] = 'eval'
        return

    # url( ... )
    elif to_parse.match('url\s*\(', wind=None):
        return parse_url(current, to_parse)

    # it's a "value" (letters, digits, -, _, #)
    elif to_parse.match('\s*([A-Za-z0-9\-_#,\.\+]*)\s*(;|})'):
        current['value_type'] = 'value';
        current['value'] = to_parse.match_group(1).strip()

        if current['value'] == '':
            current['value'] = None

        to_parse.rewind(to_parse.match_group(2))

    # function call (handle like eval( ... ) but without eval() ;) )
    else:
        value = parse_eval(to_parse)

        if not to_parse.match('\s*'):
            raise ParseError(to_parse, 'Error parsing eval statement')

        current['value'] = value
        current['value_type'] = 'eval'
        return

    return
