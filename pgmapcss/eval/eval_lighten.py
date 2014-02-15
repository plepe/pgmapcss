def eval_lighten(param):
    if len(param) < 2:
        return ''

    colors = color_values(param[0])

    # not a valid color
    if colors is None:
        return ''

    factor = to_float(param[1])
    if factor is None:
        return ''

    # from https://github.com/yvecai/mapnik-opensnowmap.org/blob/master/offset-style/build-relations-style.py
    colors[0] = round((1 - factor) * colors[0] + factor * 255);
    colors[1] = round((1 - factor) * colors[1] + factor * 255);
    colors[2] = round((1 - factor) * colors[2] + factor * 255);

    # make sure color values are between 0..255
    colors = [
        0 if v < 0 else 255 if v > 255 else v
        for v in colors
    ]

    # re-build a color hex string
    return '#' + ''.join([ '%02x' % v for v in colors ])

# TESTS
# IN ['#123456', '0.7']
# OUT '#b8c2cc'
# IN ['#1234567f', '-0.2']
# OUT '#000b347f'
# IN ['#1234567f', '1']
# OUT '#ffffff7f'
# IN ['#123456', '0.1']
# OUT '#2a4867'
