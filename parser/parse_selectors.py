from .parse_condition import parse_condition
import re

def parse_selector_part(current, to_parse, object_class_selector='\*|[a-z_]+'):
    max_scale_denominator = 3.93216e+08;
    current['conditions']  = []
    current['pseudo_element'] = 'default'
    current['min_scale'] = 0
    current['max_scale'] = None

# parse object class (way, node, canvas, ...)
    if to_parse.match('\s*(' + object_class_selector + ')'):
        if to_parse.match_group(1) == '*':
            current['type'] = True
        else:
            current['type'] = to_parse.match_group(1)

    else:
        return None

# parse classes
    while to_parse.match('\.([a-zA-Z0-9_]+)'):
        if 'classes' in current:
            pass
        else:
            current['classes'] = []

        current['classes'].append(to_parse.match_group(1))

        current['conditions'].append({ 'op': 'has_tag', 'key': '.' + to_parse.match_group(1) })

# parse zoom level
    if to_parse.match('\|z([0-9]*)(-?)([0-9]*)'):
        if to_parse.match_group(1):
            current['max_scale'] = max_scale_denominator / 2 ** (int(to_parse.match_group(1)) - 1)

        if to_parse.match_group(1) and not to_parse.match_group(2):
            current['min_scale'] = max_scale_denominator / 2 ** (int(to_parse.match_group(1)))

        if to_parse.match_group(3):
            current['min_scale'] = max_scale_denominator / 2 ** (int(to_parse.match_group(3)))

# parse conditions - TODO
    while to_parse.match('\['):
        parse_condition(current, to_parse)

# parse pseudo classes
    while to_parse.match(':([a-zA-Z0-9_]+)'):
        if 'pseudo_classes' in current:
            pass
        else:
            current['pseudo_classes'] = []

        current['pseudo_classes'].append(to_parse.match_group(1))

# parse pseudo element
    while to_parse.match('::(\(?)([a-zA-Z0-9_\*]+)(\)?)'):
        if to_parse.match_group(1) and to_parse.match_group(3):
            current['create_pseudo_element'] = False

        current['pseudo_element'] = to_parse.match_group(2)

    return to_parse

def parse_selectors(selectors, to_parse):
    while True:
      current = {}
      parse_selector_part(current, to_parse)
      selectors.append(current)

      if not to_parse.match('\s*,'):
        return
