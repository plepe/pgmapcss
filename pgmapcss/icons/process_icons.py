import os
from pgmapcss.compiler.stat import *
from pkg_resources import *

def process_icons(style_id, args, stat, conn):
    icons_dir = style_id + '.icons'
    try:
        os.mkdir(icons_dir)
    except OSError:
        pass

    images = list(set([
        (image + '-' + size + '.svg', image + '-' + color + '-' + size + '.svg', color)
        for image in stat_property_values('icon-image', stat, value_type='value')
        for color in stat_property_values('icon-color', stat)
        for size in stat_property_values('icon-size', stat)
    ]))
    print(images)

    for image in images:
        f1 = resource_stream(__name__, 'maki/src/' + image[0])
        f2 = open(icons_dir + '/' + image[1], 'w')

        content = f1.read().decode('utf-8')
        if image[2] != '#444444':
            content = content.replace('#444444', image[2])
        f2.write(content)

        f1.close()
        f2.close()
