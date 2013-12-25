import re

def parse_properties(properties, to_parse):
    if re.match('\s*\{', to_parse):
        m = re.match('\s*\{', to_parse)
        to_parse = to_parse[len(m.group(0)):]

    while to_parse:
        current = {}

        if re.match('\s*([a-zA-Z0-9_\-]+)\s*:', to_parse):
            m = re.match('\s*([a-zA-Z0-9_\-]+)\s*:', to_parse)
            current['assignment_type'] = 'P'
            current['key'] = m.group(1)

            to_parse = to_parse[len(m.group(0)):]

        elif re.match('\s*set\s+([a-zA-Z0-9_\-\.]+)\s*=', to_parse):
            m = re.match('\s*set\s+([a-zA-Z0-9_\-\.]+)\s*=', to_parse)
            current['assignment_type'] = 'T'
            current['key'] = m.group(1)

            to_parse = to_parse[len(m.group(0)):]

        elif re.match('\s*set\s+([a-zA-Z0-9_\-\.]+)\s*;', to_parse):
            m = re.match('\s*set\s+([a-zA-Z0-9_\-\.]+)\s*;', to_parse)
            current['assignment_type'] = 'T'
            current['key'] = m.group(1)

            to_parse = 'yes;' + to_parse[len(m.group(0)):]

        elif re.match('\s*unset\s+([a-zA-Z0-9_\-\.]+)\s*;', to_parse):
            m = re.match('\s*unset\s+([a-zA-Z0-9_\-\.]+)\s*;', to_parse)
            current['assignment_type'] = 'U'
            current['key'] = m.group(1)

            to_parse = ';' + to_parse[len(m.group(0)):]
        else:
# TODO: ERROR
            pass

        if re.match('\s*(.*)\s*;', to_parse):
            m = re.match('\s*(.*)\s*;', to_parse)
            current['value_type'] = 0;
            current['value'] = m.group(1)

            to_parse = to_parse[len(m.group(0)):]
        else:
# TODO: ERROR
            pass

        properties.append(current)

        if re.match('\s*\}', to_parse):
            m = re.match('\s*\}', to_parse)
            to_parse = to_parse[len(m.group(0)):]
            return to_parse

    return to_parse
