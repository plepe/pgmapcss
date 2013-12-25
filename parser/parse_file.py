from .parse_selectors import parse_selectors

class File:
    pass

def parse_file(file):
    content = open(file).read()
    to_parse = content
    stat = File()
    stat.selectors = []

    while(to_parse):
        selectors = []
        to_parse = parse_selectors(selectors, to_parse)
        stat.selectors += selectors

    return stat
