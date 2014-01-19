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

        elif m.group(2) == '':
            v = int(p)

        else:
            v = round(float(m.group(1)) * 255)

        values.append(v)

    return '#' + ''.join([ '%02x' % v for v in values ])
