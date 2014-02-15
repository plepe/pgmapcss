def eval_deluma(param):
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
    colors[0] = round(colors[0] * (1 - 0.30 * factor))
    colors[1] = round(colors[1] * (1 - 0.59 * factor))
    colors[2] = round(colors[2] * (1 - 0.11 * factor))

    # make sure color values are between 0..255
    colors = [
        0 if v < 0 else 255 if v > 255 else v
        for v in colors
    ]

    # re-build a color hex string
    return '#' + ''.join([ '%02x' % v for v in colors ])

# TESTS
# IN ['#123456', '0.7']
# OUT '#0e1f4f'
# IN ['#1234567f', '-0.2']
# OUT '#133a587f'
# IN ['#1234567f', '1']
# OUT '#0d154d7f'
# IN ['#123456', '5']
# OUT '#000027'
# IN ['#123456', '-20']
# OUT '#7effff'
