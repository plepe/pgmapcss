import os
import math
from pkg_resources import *

def build_symbol(x, stat):
    shapes = { 'triangle': 3, 'square': 4, 'pentagon': 5, 'hexagon': 6, 'heptagon': 7, 'octagon': 8, 'nonagon': 9, 'decagon': 10, 'circle': None }

    if x['symbol-shape'] not in shapes:
        print('Warning: invalid shape {symbol-shape}'.format(x))
        return None

    dest = 'symbol-{symbol-shape}-{symbol-size}-{symbol-stroke-width}-{symbol-stroke-color}-{symbol-stroke-opacity}-{symbol-fill-color}-{symbol-fill-opacity}.svg'.format(**x)

    file = 'template.svg'
    if x['symbol-shape'] == 'circle':
        file = 'template-circle.svg'

    try:
        f1 = resource_stream(__name__, file)
    except IOError:
        print('Warning: Can\'t read image symbols/{}'.format(file))
        return None

    f2 = open(stat['symbols_dir'] + '/' + dest, 'w')

    if x['symbol-shape'] == 'square':
        x['symbol-size'] = float(x['symbol-size']) * math.sqrt(2)

    radius_stroke = float(x['symbol-size']) / 2
    radius_fill = (float(x['symbol-size']) - float(x['symbol-stroke-width'])) / 2

    if x['symbol-shape'] == 'circle':
        x['radius-stroke'] = repr(radius_stroke)
        x['radius-fill'] = repr(radius_fill)

    else:
        x['fill-path'] = "M ";
        x['stroke-path'] = "M ";

        corners = shapes[x['symbol-shape']]
        step = (math.pi * 2) / corners
        pos = 0.0
        if corners % 2 == 0:
            pos = math.pi / corners

        while pos < math.pi * 2:
            x['fill-path'] += repr(math.sin(pos) * radius_fill) + "," +\
                              repr(-math.cos(pos) * radius_fill) + " "
            x['stroke-path'] += repr(math.sin(pos) * radius_stroke) + "," +\
                                repr(-math.cos(pos) * radius_stroke) + " "
            pos += step

        x['fill-path'] += "z";
        x['stroke-path'] += "z";

    content = f1.read().decode('utf-8')
    content = content.format(**x)

    f2.write(content)

    f1.close()
    f2.close()

    return dest

def init(stat):
    stat.add_generated_property(
        'final-symbol-image',
        { 'symbol-shape', 'symbol-size', 'symbol-stroke-width', 'symbol-stroke-color', 'symbol-stroke-opacity', 'symbol-fill-color', 'symbol-fill-opacity' },
        lambda x, stat: build_symbol(x, stat)
    )

def process_symbols(style_id, args, stat, conn):
    symbols_dir = style_id + '.icons'
    try:
        os.mkdir(symbols_dir)
    except OSError:
        pass

    stat['symbols_dir'] = symbols_dir
    images = stat.property_values('final-symbol-image', value_type='value')
