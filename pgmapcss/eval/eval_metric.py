def eval_metric(param):
    if len(param) == 0 or param[0] is None:
        return ''

    value = param[0].strip()
    unit = None

    if value == '':
        return ''

    m = re.match('(.*)(px|u|m)$', value)
    if m:
        value = m.group(1).strip()
        unit = m.group(2)

    try:
        value = float(value)
    except ValueError:
        return ''

    if unit == 'px' or unit is None:
        # no conversion necessary
        pass

    elif unit in ('u', 'm'):
        value = value / (0.00028 * render_context['scale_denominator'])

    else:
        return ''

    if len(param) > 1:
        if param[1] == 'px':
            # no conversion necessary
            pass

        elif param[1] in ('u', 'm'):
            value = value * (0.00028 * render_context['scale_denominator'])

        else:
            return ''

    return '%G' % value

# TESTS
# IN ['5px']
# OUT '5'
# IN ['5']
# OUT '5'
# IN ['5.0']
# OUT '5'
