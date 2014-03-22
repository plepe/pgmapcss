class config_eval_rgba(config_base):
    mutable = 3

def eval_rgba(param):
    if len(param) < 4:
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
# IN ['255', '100%', '1.0', '1.0']
# OUT '#ffffffff'
# IN ['255', '255', '255', '255']
# OUT '#ffffffff'
# IN ['1024', '-5', '127', '0']
# OUT '#ff007f00'
# IN ['1', '2', '3', '4']
# OUT '#01020304'
