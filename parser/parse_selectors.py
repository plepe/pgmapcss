import re

def parse_selector_part(current, to_parse, object_class_selector='\s|[a-z_]+'):
    max_scale_denominator = 3.93216e+08;
    current['conditions']  = []
    current['pseudo_element'] = 'default'

# parse object class (way, node, canvas, ...)
    m = re.match('\s*(' + object_class_selector + ')', to_parse)
    if m:
        if m.group(1) == '*':
            pass
        else:
            current['type'] = m.group(1)

        to_parse = to_parse[len(m.group(0)):]
    else:
        return None

# parse classes
    while re.match('\.([a-zA-Z0-9_]+)', to_parse):
        m = re.match('\.([a-zA-Z0-9_]+)', to_parse)

        if 'classes' in current:
            pass
        else:
            current['classes'] = []

        current['classes'].append(m.group(1))

        current['conditions'].append(('has_tag', '.' + m.group(1)))

        to_parse = to_parse[len(m.group(0)):]

# parse zoom level
    if re.match('\|z([0-9]*)(-?)([0-9]*)', to_parse):
        m = re.match('\|z([0-9]*)(-?)([0-9]*)', to_parse)

        if m.group(1):
            current['max_scale'] = max_scale_denominator / 2 ** (int(m.group(1)) - 1)

        if m.group(1) and not m.group(2):
            current['min_scale'] = max_scale_denominator / 2 ** (int(m.group(1)))

        if m.group(3):
            current['min_scale'] = max_scale_denominator / 2 ** (int(m.group(3)))

        to_parse = to_parse[len(m.group(0)):]

# parse conditions - TODO

# parse pseudo classes
    while re.match(':([a-zA-Z0-9_]+)', to_parse):
        m = re.match(':([a-zA-Z0-9_]+)', to_parse)

        if 'pseudo_classes' in current:
            pass
        else:
            current['pseudo_classes'] = []

        current['pseudo_classes'].append(m.group(1))

        to_parse = to_parse[len(m.group(0)):]

# parse pseudo element
    while re.match('::(\(?)([a-zA-Z0-9_\*]+)(\)?)', to_parse):
        m = re.match('::(\(?)([a-zA-Z0-9_\*]+)(\)?)', to_parse)

        if m.group(1) and m.group(3):
            current['create_pseudo_element'] = False

        current['pseudo_element'] = m.group(2)

        to_parse = to_parse[len(m.group(0)):]

    return to_parse

def parse_selectors(selectors, to_parse):
    current = {}
    to_parse = parse_selector_part(current, to_parse)
    selectors.append(current)
    return to_parse
