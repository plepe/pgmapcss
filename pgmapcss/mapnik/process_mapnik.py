import pghstore
import re
from pgmapcss.compiler.stat import *
from pkg_resources import *
import pgmapcss.db as db
unresolvable_properties = set()

def properties_values(key, stat):
    if key == 'final-casing-width':
        # build unique list of all width / casing-width combinations
        return list(set([ '%g' % (float(width or '0') + 2 * float(casing_width or '0')) \
            for width in properties_values('width', stat) \
            for casing_width in properties_values('casing-width', stat) \
        ]))

    values = stat_property_values(key, stat)

    if True in values:
        values = { v for v in values if v is not True }
        unresolvable_properties.add(key)

    return values

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
        r = r.decode('utf-8')

        if not r:
            break;

        elif re.match('# FOR\s', r):
            m = re.match('# FOR\s*(.*)', r)
            k = m.group(1).split(' ')
            combinations_list = tag_combinations(k, stat, base=replacement)
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

    return text

def process_mapnik(style_id, args, stat, conn):
    f1 = resource_stream(__name__, args.base_style + '.mapnik')
    f2 = open(style_id + '.mapnik', 'w')

    replacement = {
        'style_id': style_id,
        'host': args.host,
        'password': args.password,
        'database': args.database,
        'user': args.user
    }

    replacement['columns'] = ', '.join([
        'properties->' + db.format(prop) + ' as ' + db.ident(prop)
        for prop in stat_properties(stat)
    ])

    # dirty hack - when render_context.bbox is null, pass type 'canvas' instead of style-element
    res = db.prepare("select * from {style_id}_match(pgmapcss_render_context(null, 0), Array['canvas'])".format(**replacement))
    result = res()
    if len(result) > 0:
        canvas_properties = result[0][res.column_names.index('properties')]
        canvas_properties = pghstore.loads(canvas_properties)

        for (k, v) in canvas_properties.items():
            replacement['canvas|' + k] = v or ''

    f2.write(process(f1, replacement, stat))

    f1.close()
    f2.close()

    print('File ' + style_id + '.mapnik successfully written.')

    if len(unresolvable_properties):
        print('WARNING: Not all values for the following properties could be guessed (e.g. as they are the result of an eval-expression, and therefore some features in the resulting image(s) may be missing: ' + ', '.join(unresolvable_properties))
