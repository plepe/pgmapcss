import re
from .parse_string import parse_string

def strip_comments(content):
    done = ''
    i = 0

    while True:
        m = re.match('([^\'"/]*)([\'"/])', content)
        if not m:
            return done + content
        c = m.group(2) # c is the parsed character

        # check if character is escaped -> accept as 'normal' character
        esc = re.search('(\\\\+)$', m.group(1))
        if esc and len(esc.group(1)) % 2 == 1:
            done += m.group(0)
            content = content[len(m.group(0)):]

            continue;

        # text before parsed character is already done
        done += m.group(1)
        content = content[len(m.group(1)):]

        if c == '/':
            if re.match('//([^\n]*)\n', content):
                m1 = re.match('//([^\n]*)\n', content)
                content = content[len(m1.group(0)):]

            elif re.match('/\*.*\*/', content):
                m1 = re.match('/\*.*\*/', content)
                content = content[len(m1.group(0)):]

            else:
                done += c
                content = content[1:]

        elif c == '"' or c == "'":
            s = parse_string(content)

            done += s[2]
            content = s[1]
