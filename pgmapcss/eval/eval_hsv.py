# based on http://ubuntuforums.org/showthread.php?t=1644188&p=10232306#post10232306
class config_eval_hsv(config_base):
    mutable = 3
    alias = ( 'hsv_color' )

def eval_hsv(param, current):
    if len(param) < 3:
        return ''

    try:
        h = float(param[0])
    except:
        return ''

    values = [ 0.0, 0.0 ]
    for i, p in enumerate(param[1:3]):
        m = re.match('\s*([0-9]+(\.[0-9]+)?)(%)?\s*$', p)

        if not m:
            v = 0.0

        elif m.group(3) == '%':
            v = float(m.group(1)) / 100.0

        elif m.group(2) is None:
            v = int(p) / 100.0

        else:
            v = float(m.group(1))

        if v > 1.0:
            v = 1.0
        elif v < 0:
            v = 0

        values[i] = v

    s = values[0]
    v = values[1]

    while h > 360.0:
        h -= 360.0
    while h < 0.0:
        h += 360.0

    h /= 60.0

    i = int(math.floor(h))

    f = h - i
    p = v * (1.0 - s) * 255.0
    q = v * (1.0 - (s * f)) * 255.0
    t = v * (1.0 - (s * (1.0 - f))) * 255.0
    v = math.floor(v * 255.0)

    rgb = [[v,t,p],[q,v,p],[p,v,t],[p,q,v],[t,p,v],[v,p,q]][i]

    return '#' + ''.join([ '%02x' % int(c) for c in rgb ])

# TESTS
# IN ['180', '0.5', '0.5']
# OUT '#3f7f7f'
# IN ['180', '50', '50']
# OUT '#3f7f7f'
# IN ['120', '100', '100']
# OUT '#00ff00'
# IN ['120', '100', '0']
# OUT '#000000'
# IN ['120', '0', '100']
# OUT '#ffffff'
# IN ['120', '20', '50']
# OUT '#667f66'
# IN ['0', '100', '100']
# OUT '#ff0000'
# IN ['0', '0', '0']
# OUT '#000000'
