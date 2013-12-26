def process_mapnik(style_id, args, stat):
    f1 = open('mapnik/mapnik-2.0.mapnik', 'r')
    f2 = open(style_id + '.mapnik', 'w')

    replacement = {
        'style_id': id,
        'host': args.host,
        'password': args.password,
        'database': args.database,
        'user': args.user
    }

    while True:
        r = f1.readline()

        if not r:
            break;

        r = r.format(**replacement)

        f2.write(r)

    f1.close()
    f2.close()
