def process_mapnik(style_id, stat):
    f1 = open('mapnik/mapnik-2.0.mapnik', 'r')
    f2 = open(style_id + '.mapnik', 'w')

    while True:
        r = f1.readline()

        if not r:
            break;

        f2.write(r)

    f1.close()
    f2.close()
