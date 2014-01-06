import re
from .parse_string import parse_string

def strip_comments(to_parse):
    done = ''
    i = 0

    while True:
        if not to_parse.match('([^\'"/]*)([\'"/])', wind=None):
            return done + to_parse.to_parse()

        t = to_parse.match_group(0)
        g = to_parse.match_groups()
        c = g[1] # c is the parsed character

        # check if character is escaped -> accept as 'normal' character
        esc = re.search('(\\\\+)$', g[0])
        if esc and len(esc.group(1)) % 2 == 1:
            done += t
            to_parse.wind(len(t))

            continue;

        done += g[0]
        to_parse.wind(g[0])

        if c == '/':
            if to_parse.match('//([^\n]*)\n'):
                done += ' ' * (len(to_parse.match_group(0)) - 1) + '\n'

            elif to_parse.match('/\*.*\*/'):
                done += ' ' * len(to_parse.match_group(0))

            else:
                done += c
                to_parse.wind(1)

        elif c == '"' or c == "'":
            p = to_parse.pos()
            s = parse_string(to_parse)

            if s == None:
                raise Exception('striping comments: error parsing string')

            l = to_parse.pos() - p

            to_parse.rewind(l)
            done += to_parse.wind(l)
