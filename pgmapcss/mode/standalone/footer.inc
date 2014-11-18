# START debug.explain_queries
    sys.stderr.write('Database queries. Explained plans and statistics:\n')
    for k, v in plpy.explain_queries.items():
        sys.stderr.write('* {{}}\n'.format(k))
        sys.stderr.write('- Executed {{count}} time(s)\n'.format(**v))
        sys.stderr.write('- Explain:\n')
        for e in v['explain']:
            sys.stderr.write('    ' + e[0] + '\n')
# END debug.explain_queries

if __name__ == '__main__':
    import re
    import json
    import os

    if 'GATEWAY_INTERFACE' in os.environ:
        import cgi
        params = cgi.FieldStorage()
        args = {{ }}

        bounds = params.getvalue("bbox")
        if bounds:
            bounds = bounds.split(',')
            if len(bounds) != 4:
                print("Error parsing bounds, expecting four numbers.")
                sys.exit(1)

        parameters = {{ }}

        # using zoom/x/y
        if params.getvalue('x') and params.getvalue('y') and params.getvalue('zoom'):
            import math
            x = int(params.getvalue('x'))
            y = int(params.getvalue('y'))
            n = 2.0 ** int(params.getvalue('zoom'))
            bounds = [
                x / n * 360.0 - 180.0,
                math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n)))),
                (x + 1) / n * 360.0 - 180.0,
                math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))
            ]
            parameters['in.srs'] = 4326

        scale_denom = 2000
        if params.getvalue("zoom"):
            zoom = int(params.getvalue("zoom"))

            scale_denom = 559082264.028 / (2 ** zoom)
        if params.getvalue("z"):
            zoom = int(params.getvalue("z"))
            if params.getvalue("tilesize"):
                zoom = zoom + int(math.log(int(params.getvalue("tilesize")) / 256, 2))
            scale_denom = 559082264.028 / (2 ** zoom)
        if params.getvalue("scale"):
            scale_denom = float(params.getvalue("scale"))

        for key in params.keys():
            if key not in ('bbox', 'scale', 'zoom'):
                parameters[key] = params.getvalue(key)

        if not 'lang' in parameters:
            accept_lang = os.getenv('HTTP_ACCEPT_LANGUAGE')
            parameters['lang'] = accept_lang.split(',')[0].split(';')[0].split('_')[0]
        parameters['srs'] = {srs}
        if params.getvalue('srs'):
            parameters['srs'] = int(params.getvalue('srs'))

        # print HTML headers
        print("content-type: text/javascript, charset-utf8")
        print()

    else:
        import argparse

        # Handle negative values in --bounds parameter
        # thanks to http://stackoverflow.com/a/21446783
        for i, arg in enumerate(sys.argv):
            if (arg[0] == '-') and arg[1].isdigit(): sys.argv[i] = ' ' + arg

        parser = argparse.ArgumentParser(description='Executes the compiled map style and prints resulting objects.')

        parser.add_argument('-d', '--database', dest='database',
            help='Name of database (default: as set at compile time)')

        parser.add_argument('-u', '--user', dest='user',
            help='User for database (default: as set at compile time)')

        parser.add_argument('-p', '--password', dest='password',
            help='Password for database (default: as set at compile time)')

        parser.add_argument('-H', '--host', dest='host',
            help='Host for database (default: as set at compile time)')

        parser.add_argument('-b', '--bounds', dest='bounds',
            help='Process the map from the specified bounding box as min_lon,min_lat,max_lon,max_lat in WGS-84. (default: whole database)'
        )

        parser.add_argument('-s', '--scale', dest='scale',
            default='2000',
            help='Process map at a specified scale denominator. If z<zoom> syntax (e.g. "z15") is used, the zoom levels of projection 900913 are used.'
        )

        parser.add_argument('-P', '--parameters', dest='parameters', nargs='+',
            help='Pass the following parameters as key-value pairs to the MapCSS code, e.g. "-P foo=bar test=\'Hello World!\''
        )

        parser.add_argument('--lang', dest='lang',
            help='Use the given language code (e.g. "en" or "de") for language dependend instruction (e.g. function lang(), text:auto, ...). Default: language from current locale $LANG (or "en").'
        )

        parser.add_argument('--srs', dest='srs',
            default='4326',
            help='Use the specified spatial reference system for returned geometries (default: 4326).'
        )

        args = parser.parse_args()

        if args.bounds:
            bounds = args.bounds.split(',')
            if len(bounds) != 4:
                print("Error parsing bounds, expecting four numbers.")
                sys.exit(1)
        else:
            bounds = None

        if args.scale[0] == 'z':
            scale_denom = 559082264.028 / (2 ** int(args.scale[1:]))
        elif re.match('[0-9]+(\.[0-9]+)?$', args.scale):
            scale_denom = float(args.scale)
        else:
            print("Error parsing scale.")
            sys.exit(1)

        parameters = {{ }}
        if args.parameters is not None:
            parameters = {{
                p[0:p.find('=')]: p[p.find('=')+1:]
                for p in args.parameters
            }}

        parameters['srs'] = int(args.srs)

        if args.lang:
            parameters['lang'] = args.lang
        elif 'lang' in parameters:
            pass
        else:
            lang = os.environ.get('LANG')
            if lang:
                m = re.match('(.*)_', lang)
                if m:
                    parameters['lang'] = m.group(1)
            else:
                # default: english
                parameters['lang'] = 'en'

    plpy = fake_plpy(args)
    plpy.execute(plpy.prepare('begin', []), [])
    plan_to_geojson = plpy.prepare('select ST_asGeoJSON($1) as r', [ 'geometry' ])

    def format_result(results):
        object = results[-1]['object']

        properties_list = dict(results[-1]['tags'])
        properties_list['results'] = []

        for result in results:
            props = result['properties']
            props['pseudo_element'] = result['pseudo_element']
            if result['geo'] != object['geo']:
                g = plpy.execute(plan_to_geojson, [ result['geo'] ])[0]['r']
                props['geometry'] = json.loads(g) if g else None,

            properties_list['results'].append(props)

        geo = plpy.execute(plan_to_geojson, [ object['geo'] ])[0]['r']
        feature = {{
            'type': 'Feature',
            'geometry': json.loads(geo) if geo else None,
            'properties': properties_list,
        }}

        return json.dumps(feature, indent=2)


    results = []
    last_object = None

    for result in pgmapcss_{style_id}(bounds, scale_denom, parameters):
        if result['object'] == last_object:
            results.append(result)

        else:
            if len(results) == 0:
                print('{{ "type": "FeatureCollection",')
                print('"crs": {{ "type": "name", "properties": {{ "name": "EPSG:' + str(parameters['srs']) + '" }} }},')
                print('"features": [')
            else:
                print(format_result(results))
                print(",")

            results = [result]
            last_object = result['object']

    if len(results) == 0:
        print('{{ "type": "FeatureCollection", "features": []}}')
    else:
        print(format_result(results))
        print("]}}\n")

    plpy.execute(plpy.prepare('commit', []), [])
