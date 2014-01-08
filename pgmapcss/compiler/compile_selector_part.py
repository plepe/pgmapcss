from .compile_conditions import compile_conditions

def compile_selector_part(selector, stat, prefix='current.'):
    ret = []

    if selector['type'] != True:
        ret.append('\'' + selector['type'] + '\'=ANY(' + prefix + 'types)')

    if 'min_scale' in selector and selector['min_scale'] != 0:
        ret.append('render_context.scale_denominator >= ' + str(selector['min_scale']))

    if 'max_scale' in selector and selector['max_scale'] != None:
        ret.append('render_context.scale_denominator < ' + str(selector['max_scale']))

    # no support for pseudo classes yet -> ignore statement
    if ('pseudo_classes' in selector) and (len(selector['pseudo_classes']) > 0):
        ret.append('false')

    ret.append(compile_conditions(selector['conditions'], stat, prefix=prefix))

    if len(ret) == 0:
        return 'true'

    return ' and '.join(ret)
