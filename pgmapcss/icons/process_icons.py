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
        (image + '-24.svg', image + '-24.svg')
        for image in stat_property_values('icon-image', stat, value_type='value')
#        for casing_width in properties_values('casing-width', stat)
    ]))

    for image in images:
        f1 = resource_stream(__name__, 'maki/src/' + image[0])
        f2 = open(icons_dir + '/' + image[1], 'w')

        f2.write(f1.read().decode('utf-8'))

        f1.close()
        f2.close()
