class config_eval_green(config_base):
    mutable = 3

def eval_green(param, current):
    if len(param) == 0:
        return ''

    colors = color_values(param[0])

    if not colors:
        return ''

    return float_to_str(colors[1] / 255.0)

# TESTS
# IN ['#ff0000']
# OUT '0'
# IN ['#00ff00']
# OUT '1'
# IN ['#0000ff']
# OUT '0'
# IN ['#0000ff7f']
# OUT '0'
# IN ['#007f00']
# OUT '0.4980392156862745'
