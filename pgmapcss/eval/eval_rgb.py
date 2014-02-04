def eval_rgb(param):
    if len(param) < 3:
        return ''

    values = []

    for p in param:
        m = re.match('\s*([0-9]+(\.[0-9]+)?)(%)?\s*$', p)

        if not m:
            v = 0

        elif m.group(3) == '%':
            v = round(float(m.group(1)) * 2.55)

        elif m.group(2) is None:
            v = int(p)

        else:
            v = round(float(m.group(1)) * 255)

        if v > 255:
            v = 255
        elif v < 0:
            v = 0

        values.append(v)

    return '#' + ''.join([ '%02x' % v for v in values ])

# TESTS
# IN ['255', '100%', '1.0']
# OUT '#ffffff'
# IN ['255', '255', '255']
# OUT '#ffffff'
# IN ['1024', '-5', '127']
# OUT '#ff007f'
# IN ['1', '2', '3']
# OUT '#010203'
