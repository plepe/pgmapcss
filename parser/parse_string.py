import re

parse_string_repl = { 'n': '\n' }

def parse_string(content):
    done = ''
    parsed = ''
    pos = 0

    c = content[0]
    if c != '"' and c != "'":
        return [ None, content, None ]

    pos = 1
    esc = False
    parsed += c

    while pos < len(content):
        parsed += content[pos]

        if esc:
            t = content[pos]
            esc = False

            if t in parse_string_repl:
                done += parse_string_repl[t]
            else:
                done += t

        else:
            if content[pos] == '\\':
                esc = True
            elif content[pos] == c:
                return [ done, content[pos + 1:], parsed ]
            else:
                done += content[pos]

        pos = pos + 1

    return [ done, '', parsed ]
