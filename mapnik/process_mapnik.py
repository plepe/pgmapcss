import pghstore
import re
from compiler.stat import *
import pg

def properties_values(key, stat):
    if key == 'final-casing-width':
        # build unique list of all width / casing-width combinations
        return list(set([ str(float(width or '0') + 2 * float(casing_width or '0')) \
            for width in properties_values('width', stat) \
            for casing_width in properties_values('casing-width', stat) \
        ]))

    if not key in stat['properties_values']:
        return ['']

    else:
        return stat['properties_values'][key]

def tag_combinations(keys, stat, base={}):
    combinations_list = [base.copy()]

    for k in keys:
        new_combinations_list = []

        for combination in combinations_list:
            for v in properties_values(k, stat):
                c = combination.copy()
                c[k] = v
                new_combinations_list.append(c)

        combinations_list = new_combinations_list

    return combinations_list

def process(f1, replacement, stat, rek=0):
    text = ''

    while True:
        r = f1.readline()

        if not r:
            break;

        elif re.match('# FOR\s', r):
            m = re.match('# FOR\s*(.*)', r)
            k = m.group(1).split(' ')
            combinations_list = tag_combinations(k, stat, base=replacement)
            f1_pos = f1.tell()

            for c in combinations_list:
                f1.seek(f1_pos)
                text += process(f1, c, stat, rek + 1)

        elif re.match('# END', r):
            break;

        else:
            text += r.format(**replacement)

    return text

def process_mapnik(style_id, args, stat, db):
    f1 = open('mapnik/mapnik-2.0.mapnik', 'r')
    f2 = open(style_id + '.mapnik', 'w')

    replacement = {
        'style_id': style_id,
        'host': args.host,
        'password': args.password,
        'database': args.database,
        'user': args.user
    }

    replacement['columns'] = ', '.join([
        'properties->' + pg.format(prop) + ' as ' + pg.ident(prop)
        for prop in stat_properties(stat)
    ])

    print("select * from {style_id}_check(pgmapcss_object('', '', null, Array['canvas']), pgmapcss_render_context(null, null))".format(**replacement))
    res = db.prepare("select * from {style_id}_check(pgmapcss_object('', '', null, Array['canvas']), pgmapcss_render_context(null, null))".format(**replacement))
    result = res()
    if len(result) > 0:
        canvas_properties = result[0][res.column_names.index('properties')]
        canvas_properties = pghstore.loads(canvas_properties)

        for (k, v) in canvas_properties.items():
            replacement['canvas|' + k] = v or ''

    f2.write(process(f1, replacement, stat))

    f1.close()
    f2.close()
