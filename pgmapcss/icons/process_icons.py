import os
from pkg_resources import *

def build_icon(x, stat):
    if os.path.exists(stat['dir_name'] + '/' + x['icon-image']):
        os.copy(stat['dir_name'] + '/' + x['icon-image'], stat['icons_dir'] + '/' + x['icon-image'])

        return stat['icons_dir'] + '/' + x['icon-image']

    if True in x.values():
        return True

    src = x['icon-image'] + '-' + x['icon-width'] + '.svg'
    dest = x['icon-image'] + '-' + x['icon-color'] + '-' + x['icon-width'] + '.svg'

    if not 'icons_dir' in stat:
        return dest

    try:
        f1 = resource_stream(__name__, 'maki/' + src)
    except IOError:
        print('Warning: Can\'t read image {}'.format(src))
        return dest

    f2 = open(stat['icons_dir'] + '/' + dest, 'w')

    content = f1.read().decode('utf-8')
    if x['icon-color'] != '#444444':
        content = content.replace('#444444', x['icon-color'])
    f2.write(content)

    f1.close()
    f2.close()

    return dest

def init(stat):
    stat.add_generated_property(
        'final-icon-image',
        { 'icon-image', 'icon-width', 'icon-color' },
        lambda x, stat: build_icon(x, stat)
    )

def process_icons(style_id, args, stat, conn):
    images = stat.property_values('final-icon-image', value_type='value', eval_true=False, warn_unresolvable=True)
