import pgmapcss.types
from .compile_eval import compile_eval

def compile_build_result(stat):
    indent = '    '

    ret  = '''\
def build_result(current, pseudo_element):
    has_postprocessed = set()

    # Finally build return value(s)
    ret = {
        'id': current['object']['id'],
        'types': list(current['object']['types']),
        'tags': current['tags'],
        'pseudo_element': pseudo_element
    }

'''

    # handle @values, @default_other for all properties
    done_prop = []

    # make sure, that depend_properties are compiled in the same order as
    # specified in the mapcss file
    main_prop_order = [
        k
        for k, d in stat['defines']['depend_property'].items()
    ]
    def main_prop_order_key(k):
        return stat['defines']['depend_property'][k]['pos']
    main_prop_order.sort(key=main_prop_order_key)

    stat['may_have_postprocessed'] = set()
    # start with props from @depend_property
    for main_prop in main_prop_order:
        props = stat['defines']['depend_property'][main_prop]
        include_main_prop = False
        if main_prop in stat.properties():
            include_main_prop = True

        props = props['value'].split(';')
        r = ''

        # main_prop never been used -> skip
        if include_main_prop:
            r += print_checks(main_prop, stat, indent=indent + '    ')
            r += print_postprocess(main_prop, stat, indent=indent + '    ')

        done_prop.append(main_prop)

        for prop in props:
            if include_main_prop:
                r += print_checks(prop, stat, main_prop=main_prop, indent=indent + '    ')

            done_prop.append(prop)

        # finally, post process values
        if include_main_prop:
            for prop in props:
                r += print_postprocess(prop, stat, indent=indent + '    ')
            r += print_postprocess(main_prop, stat, indent=indent + '    ')

        if include_main_prop and r != '':
            ret += indent + 'if ' + repr(main_prop) + " in current['properties'][pseudo_element]:\n"
            ret += r

    for prop in [ prop for prop in stat.properties() if not prop in done_prop ]:
        ret += print_checks(prop, stat, indent=indent)
        ret += print_postprocess(prop, stat, indent=indent)

    ret += indent + '''\
ret['properties'] = current['properties'][pseudo_element]

return ret
'''.replace('\n', '\n' + indent)

    return ret

def print_postprocess(prop, stat, indent=''):
    ret = ''

    # tag type specific stuff
    prop_type = pgmapcss.types.get(prop, stat)
    r = prop_type.compile_postprocess()
    if r:
        ret += '\n'.join(indent + x for x in r.splitlines()) + '\n'

    # postprocess requested properties (see @postprocess)
    if prop in stat['defines']['postprocess']:
        v = stat['defines']['postprocess'][prop]
        res = compile_eval(v['value'], v, stat)
        ret += indent + "current['properties'][pseudo_element][" + repr(prop) +\
           "] = " + res['code'] + '\n'

    # if property has been postprocessed (because it is ad depending property
    # in several main properties), don't process again
    if ret != '':
        if prop in stat['may_have_postprocessed']:
            ret = indent + 'if not ' + repr(prop) + ' in has_postprocessed:\n' +\
                  '\n'.join('    ' + x for x in ret.splitlines()) + '\n'

        ret += indent + 'has_postprocessed.add(' + repr(prop) + ')\n'
        stat['may_have_postprocessed'].add(prop)

    return ret

def get_default_other(prop, stat):
    ret = "(current['properties'][pseudo_element][" + repr(prop) + "] if " + repr(prop) + " in current['properties'][pseudo_element] else "

    if 'default_other' in stat['defines'] and prop in stat['defines']['default_other']:
        ret += get_default_other(stat['defines']['default_other'][prop]['value'], stat)

    elif 'default_value' in stat['defines'] and prop in stat['defines']['default_value']:
        ret += repr(stat['defines']['default_value'][prop]['value'])

    else:
        ret += "None"

    ret += ")"

    return ret

def print_checks(prop, stat, main_prop=None, indent=''):
    ret = ''

    # @default_other
    if 'default_other' in stat['defines'] and prop in stat['defines']['default_other']:
        other = stat['defines']['default_other'][prop]['value']
        ret += indent + 'if not ' + repr(prop) + " in current['properties'][pseudo_element] or current['properties'][pseudo_element][" + repr(prop) + "] is None:\n"
        ret += indent + "    current['properties'][pseudo_element][" + repr(prop) + "] = " + get_default_other(other, stat) + "\n"

    # @default_value
    if 'default_value' in stat['defines'] and prop in stat['defines']['default_value'] and stat['defines']['default_value'][prop]['value'] is not None:
        ret += indent + 'if ' + repr(prop) + " not in current['properties'][pseudo_element]:\n" # or current['properties'][pseudo_element][" + repr(prop) + "] in (None, ''):\n"
        ret += indent + "    current['properties'][pseudo_element][" + repr(prop) + "] = " + repr(stat['defines']['default_value'][prop]['value']) + "\n"

    # @values
    if 'values' in stat['defines'] and prop in stat['defines']['values']:
        values = stat['defines']['values'][prop]['value'].split(';')
        used_values = stat.property_values(prop, include_illegal_values=True)

        # if there are used values which are not allowed, always check
        # resulting value and - if not allowed - replace by the first
        # allowed value
        if len([ v for v in used_values if not v in values ]):
            ret += indent + 'if ' + repr(prop) + " not in current['properties'][pseudo_element] or current['properties'][pseudo_element][" + repr(prop) + "] not in " + repr(values) + ":\n"

            # if a default value is defined for this property, use this.
            if 'default_value' in stat['defines'] and prop in stat['defines']['default_value']:
                default_value = repr(stat['defines']['default_value'][prop]['value'])
            # otherwise use the first of the allowed values
            else:
                default_value = repr(values[0])

            ret += indent + "    current['properties'][pseudo_element][" + repr(prop) + "] = " + default_value + '\n'

    return ret
