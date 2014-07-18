import os
from pgmapcss.compiler.stat import *
from pkg_resources import *

def build_symbol(x, stat):
    if x['symbol-shape'] not in ('square'):
        print('Warning: invalid shape {symbol-shape}'.format(x))
        return None

    print(x)
    dest = 'symbol-{symbol-shape}-{symbol-size}-{symbol-stroke-width}-{symbol-stroke-color}-{symbol-stroke-opacity}-{symbol-fill-color}-{symbol-fill-opacity}.svg'.format(**x)

    try:
        f1 = resource_stream(__name__, 'template.svg')
    except IOError:
        print('Warning: Can\'t read image symbols/template.svg')
        return None

    f2 = open(stat['symbols_dir'] + '/' + dest, 'w')

    s1 = float(x['symbol-size'])
    s2 = float(x['symbol-stroke-width']) / 2
    x['final-symbol-size'] = repr(s1 + s2 * 2)

    if x['symbol-shape'] == 'square':
        x['path'] = "M " + repr(s2) + "," + repr(s2) + " " +\
                           repr(s2 + s1) + "," + repr(s2) + " " +\
                           repr(s2 + s1) + "," + repr(s2 + s1) + " " +\
                           repr(s2) + "," + repr(s2 + s1) + " z"

    content = f1.read().decode('utf-8')
    content = content.format(**x)

    f2.write(content)

    f1.close()
    f2.close()

    return dest

def init(stat):
    stat_add_generated_property(
        'final-symbol-image',
        { 'symbol-shape', 'symbol-size', 'symbol-stroke-width', 'symbol-stroke-color', 'symbol-stroke-opacity', 'symbol-fill-color', 'symbol-fill-opacity' },
        lambda x, stat: build_symbol(x, stat),
        stat
    )

def process_symbols(style_id, args, stat, conn):
    symbols_dir = style_id + '.icons'
    try:
        os.mkdir(symbols_dir)
    except OSError:
        pass

    stat['symbols_dir'] = symbols_dir
    images = stat_property_values('final-symbol-image', stat, value_type='value')
