from .ParseError import *
from ..version import *
import re

def _check_version(check, current, comp='=='):
    if type(check) == str:
        check = re.split("[\.-]", check)
    if type(current) == str:
        current = re.split("[\.-]", current)

    for i, v in enumerate(check):
        if len(current) >= i:
            try:
                v = int(v)
            except:
                v = None

            try:
                c = int(current[i])
            except:
                c = None

            if v and c:
                if comp == '==' and v != c:
                    return False
                if comp == 'min' and v > c:
                    return False
                if comp == 'max' and v < c:
                    return False

    return True

# returns
# * the media query to include in statement (might be simplified)
# * ('media-ignore') if we can ignore the media query at parse time - if yes,
#   it will move file pointer to the end of the @media { ... } statement
def check_media_query(stat, to_parse, query):
    match = False
    for q1 in query:
        match1 = True
        negated1 = False

        if q1[0] == 'NOT':
            negated1 = True

        for q in q1[1:]:
            m1 = False
            condition_key = q[0]
            condition_value = q[1]
            minmax_condition_key = q[0]
            minmax = '=='

            q2 = re.match('((min|max)-)?(.*)$', q[0])
            if q2:
                minmax_condition_key = q2.group(3)
                minmax = q2.group(2)
            print(condition_key, minmax_condition_key, minmax, condition_value)

# add here all queries that are (or might be) True
            if condition_key == 'user-agent' and q[1] == 'pgmapcss':
                m1 = True
            elif minmax_condition_key == 'pgmapcss-version':
                m1 = _check_version(condition_value, VERSION_INFO, minmax)

            elif condition_key == 'renderer':
                m1 = (q[1] == stat['base_style'].split("-")[0])

            elif minmax_condition_key == 'renderer-version':
                m1 = _check_version(condition_value, stat['base_style'].split("-")[1], minmax)

            elif condition_key == 'type':
                m1 = True

            if not m1:
                match1 = False

        if match1 and not negated1:
            match = True
        if not match1 and negated1:
            match = True

    if match:
        return ( 'media', query )

# if match is False we can ignore the whole @media { ... } statement ...
# search for closing bracket
    mode = 0
    level = 1

    while True:
        if mode == 0:
            if to_parse.match('[^\'"{}\\\\]*([\'"{}\\\\])'):

                c = to_parse.match_group(1)
                if c == '}':
                    if level == 1:
                        return ('media-ignore')
                    else:
                        level = level - 1
                elif c == '{':
                    level = level + 1
                elif c == '\\':
                    to_parse.match('.')
                elif c == '"':
                    mode = 1
                elif c == '\'':
                    mode = 2

            elif to_parse.match('.*\n'):
                pass

        elif mode in (1, 2):
            if to_parse.match('[^\'"\\\\]*([\'"\\\\])'):

                c = to_parse.match_group(1)
                if c == '\\':
                    to_parse.match('.')
                elif (mode == 1 and c == '"') or (mode == 2 and c == '\''):
                    mode = 0

            elif to_parse.match('.*\n'):
                pass

        if not to_parse.to_parse():
            raise ParseError(to_parse, '@media query not closed at')
