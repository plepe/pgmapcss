import pghstore

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

    print("select * from {style_id}_check(pgmapcss_object('', '', null, Array['canvas']), pgmapcss_render_context(null, null))".format(**replacement))
    res = db.prepare("select * from {style_id}_check(pgmapcss_object('', '', null, Array['canvas']), pgmapcss_render_context(null, null))".format(**replacement))
    result = res()
    if len(result) > 0:
        canvas_properties = result[0][res.column_names.index('properties')]
        canvas_properties = pghstore.loads(canvas_properties)

        for (k, v) in canvas_properties.items():
            replacement['canvas|' + k] = v or ''

    while True:
        r = f1.readline()

        if not r:
            break;

        r = r.format(**replacement)

        f2.write(r)

    f1.close()
    f2.close()
