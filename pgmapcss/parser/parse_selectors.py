from .parse_condition import parse_condition
from .parse_string import parse_string
from .ParseError import *
import re

def parse_selector_part(to_parse, object_class_selector='\*|[a-z_]+'):
    max_scale_denominator = 3.93216e+08;
    current = {}
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
        raise ParseError(to_parse, 'Can\'t parse object class')

    last_pos = None

    while last_pos != to_parse.pos():
        last_pos = to_parse.pos()

# parse classes
        if to_parse.match('(!?)\.([a-zA-Z0-9_]+)'):
            if 'classes' in current:
                pass
            else:
                current['classes'] = []

            condition = {
                'op': 'has_tag',
                'key': '.' + to_parse.match_group(2)
            }

            if to_parse.match_group(1) == '!':
                condition['op'] = '! has_tag'
            else:
                current['classes'].append(to_parse.match_group(2))

            current['conditions'].append(condition)

# parse zoom level
        if to_parse.match('\|z([0-9]*)(-?)([0-9]*)'):
            if to_parse.match_group(1):
                current['max_scale'] = max_scale_denominator / 2 ** (int(to_parse.match_group(1)) - 1)

            if to_parse.match_group(1) and not to_parse.match_group(2):
                current['min_scale'] = max_scale_denominator / 2 ** (int(to_parse.match_group(1)))

            if to_parse.match_group(3):
                current['min_scale'] = max_scale_denominator / 2 ** (int(to_parse.match_group(3)))

# parse conditions - TODO
        if to_parse.match('\['):
            result = parse_condition(to_parse)
            if result:
                current['conditions'].append(result)

# parse pseudo classes
        if to_parse.match('(!?):([a-zA-Z0-9_\-]+)'):
            condition = {
                'op': 'pseudo_class',
                'key': to_parse.match_group(2)
            }

            if to_parse.match_group(1) == '!':
                condition['op'] = '! pseudo_class'

# ... additionally check if there is a parameter to the pseudo class
            if to_parse.match('\('):
                m = parse_string(to_parse)
                if m:
                    condition['value'] = m
                    to_parse.match('\)')
                elif to_parse.match('([^\)]*)\)'):
                    condition['value'] = to_parse.match_group(1)
                else:
                    raise ParseError(to_parse, 'Can\'t parse parameter to pseudo class')

            current['conditions'].append(condition)

# parse pseudo element
        if to_parse.match('::(\(?)([a-zA-Z0-9_\*\-]+)(\)?)'):
            if to_parse.match_group(1) and to_parse.match_group(3):
                current['create_pseudo_element'] = False

            current['pseudo_element'] = to_parse.match_group(2)

    return current

def parse_selectors(selectors, to_parse):
    while True:
        selector = {}
        selectors.append(selector)

        sel1 = parse_selector_part(to_parse)
        sel2 = None
        sel3 = None

        try:
            sel2 = parse_selector_part(to_parse, '>|<|near|∈|within|∋|surrounds|⧉|overlaps')
            if sel2['type'] in ('∈', '⧉', '∋'):
                sel2['type'] = { '∈': 'within', '⧉': 'overlaps', '∋': 'surrounds' }[sel2['type']]
        except ParseError:
            pass

        try:
            sel3 = parse_selector_part(to_parse)
        except ParseError:
            if sel2: # if a link selector exists we need a 3rd selector
                raise

        if sel1 and sel2 and sel3:
            selector['selector'] = sel3
            selector['selector']['parent'] = sel1
            selector['selector']['link'] = sel2

        elif sel1 and not sel2 and sel3:
            selector['selector'] = sel3
            selector['selector']['parent'] = sel1
            selector['selector']['link'] = {
                'type': '',
                'conditions': []
            }

        else:
            selector['selector'] = sel1

        if not to_parse.match('\s*,'):
            return
