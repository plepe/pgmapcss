import os
from pgmapcss.compiler.stat import *
from pkg_resources import *

def init(stat):
    stat_add_generated_property(
        'final-icon-image',
        { 'icon-image', 'icon-size', 'icon-color' },
        lambda x: (
            x['icon-image'] + '-' + x['icon-size'] + '.svg',
            x['icon-image'] + '-' + x['icon-color'] + '-' + x['icon-size'] + '.svg',
            x['icon-color']
        ),
        stat
    )

def process_icons(style_id, args, stat, conn):
    icons_dir = style_id + '.icons'
    try:
        os.mkdir(icons_dir)
    except OSError:
        pass

    images = stat_property_values('final-icon-image', stat)

    for image in images:
        f1 = resource_stream(__name__, 'maki/src/' + image[0])
        f2 = open(icons_dir + '/' + image[1], 'w')

        content = f1.read().decode('utf-8')
        if image[2] != '#444444':
            content = content.replace('#444444', image[2])
        f2.write(content)

        f1.close()
        f2.close()
