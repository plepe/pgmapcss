def compile_selector_part(selector, stat, prefix='current.'):
    ret = []

    if 'type' in selector:
        ret.append('\'' + selector['type'] + '\'=ANY(' + prefix + 'types)')

    if 'min_scale' in selector:
        ret.append('render_context.scale_denominator >= ' + str(selector['min_scale']))

    if 'max_scale' in selector:
        ret.append('render_context.scale_denominator < ' + str(selector['max_scale']))

    # no support for pseudo classes yet -> ignore statement
    if ('pseudo_classes' in selector) and (len(selector['pseudo_classes']) > 0):
        ret.append('false')

    return ' and '.join(ret)
