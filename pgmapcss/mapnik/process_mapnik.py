import pghstore
import re
from pgmapcss.compiler.stat import *
from pkg_resources import *
import pgmapcss.db as db

def init(stat):
    stat_add_generated_property(
        'final-casing-width',
        { 'width', 'casing-width' },
        lambda x, stat: '%g' % (float(x['width'] or '0') + 2 * float(x['casing-width'] or '0')),
        stat
    )

def combinations_combine(base, combinations_list):
    return [
        dict(list(base.items()) + list(b.items()))
        for b in combinations_list
    ]

    return combinations_list

def process(f1, replacement, stat, rek=0):
    text = ''

    while True:
        r = f1.readline()
        r = r.decode('utf-8')

        if not r:
            break;

        elif re.match('# FOR\s', r):
            m = re.match('# FOR\s*(.*)', r)
            k = m.group(1).split(' ')
            combinations_list = combinations_combine(replacement, stat_properties_combinations(k, stat, eval_true=False))
            f1_pos = f1.tell()

            # if no combinations found, skip to next # END
            if len(combinations_list) == 0:
                while(True):
                    r = f1.readline()
                    r = r.decode('utf-8')

                    if re.match('# END', r):
                        break;

            for c in combinations_list:
                f1.seek(f1_pos)
                text += process(f1, c, stat, rek + 1)

        elif re.match('# END', r):
            break;

        else:
            text += r.format(**replacement)

        # check for columns which need to be added to the sql query
        r1 = r
        m = re.match('[^\[]+\[([a-zA-Z0-9\-_]+)\]', r1)
        while m:
            stat['mapnik_columns'].add(m.group(1))
            r1 = r1[len(m.group(0)):]
            m = re.match('[^\[]+\[([a-zA-Z0-9\-_]+)\]', r1)

    return text

def process_mapnik(style_id, args, stat, conn):
    f1 = resource_stream(__name__, args.base_style + '.mapnik')
    f2 = open(style_id + '.mapnik', 'w')

    replacement = {
        'style_id': style_id,
        'host': args.host,
        'password': args.password,
        'database': args.database,
        'user': args.user,
        'columns': '{columns}'
    }

    stat['mapnik_columns'] = set()

    # dirty hack - when render_context.bbox is null, pass type 'canvas' instead of style-element
    res = db.prepare("select * from pgmapcss_{style_id}(null, 0, Array['canvas']) where pseudo_element='default'".format(**replacement))
    result = res()
    if len(result) > 0:
        canvas_properties = result[0][res.column_names.index('properties')]
        canvas_properties = pghstore.loads(canvas_properties)

        for (k, v) in canvas_properties.items():
            replacement['canvas|' + k] = v or ''

    text = process(f1, replacement, stat)

    # finally replace 'columns'
    replacement = {}
    replacement['columns'] = ', '.join([
        'properties->' + db.format(prop) + ' as ' + db.ident(prop)
        for prop in stat_properties(stat)
    ])

    f2.write(text.format(**replacement))

    f1.close()
    f2.close()

    print('File ' + style_id + '.mapnik successfully written.')
