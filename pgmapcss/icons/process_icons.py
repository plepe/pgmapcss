import os
from pgmapcss.compiler.stat import *
from pkg_resources import *

def build_icon(x, stat):
    src = x['icon-image'] + '-' + x['icon-size'] + '.svg'
    dest = x['icon-image'] + '-' + x['icon-color'] + '-' + x['icon-size'] + '.svg'

    f1 = resource_stream(__name__, 'maki/' + src)
    f2 = open(stat['icons_dir'] + '/' + dest, 'w')

    content = f1.read().decode('utf-8')
    if x['icon-color'] != '#444444':
        content = content.replace('#444444', x['icon-color'])
    f2.write(content)

    f1.close()
    f2.close()

    return dest

def init(stat):
    stat_add_generated_property(
        'final-icon-image',
        { 'icon-image', 'icon-size', 'icon-color' },
        lambda x, stat: build_icon(x, stat),
        stat
    )

def process_icons(style_id, args, stat, conn):
    icons_dir = style_id + '.icons'
    try:
        os.mkdir(icons_dir)
    except OSError:
        pass

    stat['icons_dir'] = icons_dir
    images = stat_property_values('final-icon-image', stat, value_type='value')
