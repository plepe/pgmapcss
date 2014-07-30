class config_eval_alpha(config_base):
    mutable = 3

def eval_alpha(param):
    if len(param) == 0:
        return ''

    colors = color_values(param[0])

    if not colors:
        return ''

    if len(colors) == 3:
        return '1'

    return float_to_str(colors[3] / 255.0)

# TESTS
# IN ['#ff0000']
# OUT '1'
# IN ['#00ff00']
# OUT '1'
# IN ['#0000ff']
# OUT '1'
# IN ['#0000ffff']
# OUT '1'
# IN ['#0000ff7f']
# OUT '0.4980392156862745'
