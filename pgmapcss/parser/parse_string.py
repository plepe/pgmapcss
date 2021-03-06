parse_string_repl = { 'n': '\n' }

def parse_string(to_parse, delim=("'", '"')):
    done = ''
    parsed = ''
    pos = 0

    if type(delim) == str:
        delim = { delim }

    if not to_parse.match("\s*(" + "|".join(delim) + ")"):
        return None
    else:
        c = to_parse.match_group(1)

    esc = False
    parsed += c

    while to_parse.to_parse():
        next_char = to_parse.to_parse()[0]
        to_parse.wind(1)

        if esc:
            t = next_char
            esc = False

            if t in parse_string_repl:
                done += parse_string_repl[t]
            else:
                done += t

        else:
            if next_char == '\\':
                esc = True
            elif next_char == c:
                return done
            else:
                done += next_char

    return done
