import pghstore
import re
from pkg_resources import *
import pgmapcss.db as db
import hashlib
import pgmapcss.eval
import pgmapcss.compiler

def strtr(s, patterns):
    keys = sorted([ k for k in patterns ], key=len, reverse=True)

    for k in keys:
        s = s.replace(k, patterns[k])

    return s

# Postgresql only supports columns names with a length of up to 64 chars
# When column names get concatenated, this could lead to problems
# For longer names replace name by its md5 sum
def shorten_column(s):
    if len(s) < 64:
        return s

    return hashlib.md5(s.encode('UTF-8')).hexdigest()

def init(stat):
    stat.add_generated_property(
        'final-casing-width',
        { 'width', 'casing-width' },
        lambda x, stat: '%g' % (float(x['width'] or '0') + 2 * float(x['casing-width'] or '0'))
    )

def sql_convert_prop(k, s, stat):
    if not k in stat['defines']['type']:
        return '(' + s + ')'

    t = stat['defines']['type'][k]['value']

    if t == 'angle' and 'angular_system' in stat['config'] and stat['config']['angular_system'] == 'radians':
        return 'cast(round(cast(degrees(cast(' + s + ' as numeric)) as numeric), 5) as text)'

    return '(' + s + ')'

def rep_convert_prop(k, v, stat):
    import math
    if not k in stat['defines']['type']:
        return v

    t = stat['defines']['type'][k]['value']

    if t == 'angle' and 'angular_system' in stat['config'] and stat['config']['angular_system'] == 'radians':
        return str(round(math.degrees(float(v)), 5))

    return v

def combinations_combine(base, combinations_list, stat):
    combinations_list = [
        {
            '{' + k + '}': rep_convert_prop(k, v, stat)
            for k, v in c.items()
        }
        for c in combinations_list
    ]

    return [
        dict(list(base.items()) + list(b.items()))
        for b in combinations_list
    ]

    return combinations_list

def process(f1, replacement, stat, rek=0):
    ret = {
        'text': '',
        'columns': set(),
    }

    while True:
        r = f1.readline()
        r = r.decode('utf-8')

        if not r:
            break;

        elif re.match('# IF\s', r):
            m = re.match('# IF\s*(.*)', r)
            keys = m.group(1).split(' ')

            # Check if all of the keys are used
            count = [
                True
                for k in keys
                if len(stat.property_values(k))
            ]

            # Process anyway ...
            res = process(f1, replacement, stat, rek + 1)

            # ... but if not used, ignore
            if len(count):
                ret['text'] += res['text']
                ret['columns'] = ret['columns'].union(res['columns'])

        elif re.match('# FOR\s', r):
            m = re.match('# FOR\s*(.*)', r)
            k = m.group(1).split(' ')

            combinations_list = combinations_combine(replacement, stat.properties_combinations(k, eval_true=False, warn_unresolvable=True), stat)
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
                res = process(f1, c, stat, rek + 1)

                ret['text'] += res['text']
                ret['columns'] = ret['columns'].union(res['columns'])

        elif re.match('# END', r):
            break;

        else:
            t = r
            if re.search('<Filter>', r):
                # find all matches for columns which occur in <Filter>. if the column name is longer than 63 chars, shorten column.
                col_match = re.findall('([^\[]*)(\[([^\]]+)\])?', r)
                t = ''
                for m in col_match:
                    if m[2] == '':
                        t += m[0]
                    else:
                        t += m[0] + '[' + shorten_column(m[2]) + ']'

            else:
                props = re.findall("\[([^\] ]+)\]", t)
                for p in props:
                    v = stat.property_values(p).copy()
# wrap-character: Mapnik 2.2 does not accept fixed values in ExpressionFormat
                    if len(v) == 1 and not True in v and stat.property_default_value(p) in v and p not in ('wrap-character'):
                        v = v.pop()
                        t = t.replace('[' + p + ']', v)
                        r = r.replace('[' + p + ']', v)

            ret['text'] += strtr(t, replacement)

        # check for columns which need to be added to the sql query
        r1 = r
        m = re.match('[^\[]+\[([a-zA-Z0-9\-_ ]+)\]', r1)
        while m:
            ret['columns'].add(m.group(1))
            r1 = r1[len(m.group(0)):]
            m = re.match('[^\[]+\[([a-zA-Z0-9\-_ ]+)\]', r1)

    return ret

def build_sql_column(props, stat):
    sql_as = shorten_column(' '.join(props))

    prop_values = {
        k: stat.property_values(k)
        for k in props
    }
    default_props = {
        k: v.copy().pop()
        for k, v in prop_values.items()
        if len(v) == 1 and stat.property_default_value(k) in v
    }

    r = []
    first = 'default'
    last = 'default'
    for k in props:
        if k in default_props and default_props[k] is not True:
            r.append(default_props[k])
            last = 'default'
        else:
            if len(r) == 0:
                first = 'query'
            last = 'query'
            r.append("' || " + sql_convert_prop(k, 'properties->' + db.format(k), stat) + " || '")

    r = "'" + ' '.join(r) + "'"

    if first == 'query':
        r = r[6:]
    if last == 'query':
        r = r[:-6]

    return r + ' as "' + sql_as + '"'

def process_renderer(style_id, args, stat, conn):
    f1 = resource_stream(__name__, args.base_style + '.mapnik')
    f2 = open(style_id + '.mapnik', 'w')

    replacement = {
        '{style_id}': style_id,
        '{host}': args.host,
        '{password}': args.password,
        '{database}': args.database,
        '{user}': args.user,
        '{columns}': '{columns}'
    }

    stat['mapnik_columns'] = set()

    # compile check function for canvas, and call to get results
    canvas = {
        'id': None,
        'tags': {},
        'geo': None,
        'types': [ 'canvas' ],
    }

    check_code = pgmapcss.compiler.compile_function_check(stat['statements'], 0, 0, stat)
    for r in pgmapcss.eval.functions(stat).eval('check_0({})'.format(canvas), additional_code=check_code):
        if r[0] == 'result':
            result = r[1]
            if result['pseudo_element'] == 'default':
                canvas_properties = result['properties']

                for (k, v) in canvas_properties.items():
                    replacement['{canvas|' + k + '}'] = v or ''

    result = process(f1, replacement, stat)

    # style-element is an extra column in result set
    result['columns'].remove('style-element')

    # finally replace 'columns'
    replacement = {}
    replacement['{columns}'] = ',\n  '.join([
        build_sql_column(props.split(' '), stat)
        for props in result['columns']
    ])

    f2.write(strtr(result['text'], replacement))

    f1.close()
    f2.close()

    print('File ' + style_id + '.mapnik successfully written.')
