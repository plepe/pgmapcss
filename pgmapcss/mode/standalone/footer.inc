# START debug.explain_queries
    sys.stderr.write('Database queries. Explained plans and statistics:\n')
    for k, v in plpy.explain_queries.items():
        sys.stderr.write('* {{}}\n'.format(k))
        sys.stderr.write('- Executed {{count}} time(s)\n'.format(**v))
        if 'explain' in v:
            sys.stderr.write('- Explain:\n')
            for e in v['explain']:
                sys.stderr.write('    ' + e[0] + '\n')
# END debug.explain_queries

if __name__ == '__main__':
    import re
    import json
    import os
    include_meta = 'false'

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

        scale_denom = 2000
        z = None
        if params.getvalue("zoom"):
            zoom = int(params.getvalue("zoom"))
            z = zoom

            if params.getvalue("tilesize"):
                z = zoom - int(math.log(int(params.getvalue("tilesize")) / 256, 2))
            scale_denom = 559082264.028 / (2 ** zoom)

        if params.getvalue("z"):
            zoom = int(params.getvalue("z"))
            z = zoom

            if params.getvalue("tilesize"):
                zoom = zoom + int(math.log(int(params.getvalue("tilesize")) / 256, 2))

            scale_denom = 559082264.028 / (2 ** zoom)

        # using z/x/y
        if params.getvalue('x') and params.getvalue('y') and z:
            import math
            x = int(params.getvalue('x'))
            y = int(params.getvalue('y'))
            n = 2.0 ** z
            bounds = [
                x / n * 360.0 - 180.0,
                math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n)))),
                (x + 1) / n * 360.0 - 180.0,
                math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))
            ]
            parameters['in.srs'] = 4326

        if params.getvalue("id"):
            bounds = set(params.getlist("id"))

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

        if 'meta' in parameters:
            include_meta = parameters['meta']

        if bounds is None and include_meta != 'only':
            print("No bounding box defined.")
            sys.exit(1)

        # re-open stdout to use utf-8 encoding
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

        # print HTML headers
        print("content-type: application/javascript; charset=utf-8")
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
            help='Process the map from the specified bounding box as min_lon,min_lat,max_lon,max_lat in WGS-84. If you pass \'all\', the whole database will be queried.'
        )

        parser.add_argument('-o', '--id', dest='id', nargs='+',
            help='Instead of processing all objects in the specified bounding box, process only the given object(s).')

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

        parser.add_argument('--meta', dest='meta',
            default='true',
            help='Whether meta information should be included (true, false, only)'
        )

        args = parser.parse_args()

        if args.bounds:
            if args.bounds == 'all':
                bounds = None
            else:
                bounds = args.bounds.split(',')
                if len(bounds) != 4:
                    print("Error parsing argument 'bounds', expecting four numbers or 'all'.")
                    sys.exit(1)

        elif args.id:
            bounds = set(args.id)

        else:
            print("Argument 'bounds' not defined, expecting four numbers or 'all'")
            sys.exit(1)

        if args.scale[0] == 'z':
            scale_denom = 559082264.028 / (2 ** int(args.scale[1:]))
        elif re.match('[0-9]+(\.[0-9]+)?$', args.scale):
            scale_denom = float(args.scale)
        else:
            print("Error parsing scale.")
            sys.exit(1)

        include_meta = args.meta

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

        return json.dumps(feature, indent=4, ensure_ascii=False)


    results = []
    last_object = None

    if include_meta in ('true', 'only'):
        meta = {{}}
        for result in pgmapcss_{style_id}('meta', scale_denom, parameters):
            meta = result
        meta['id'] = '{style_id}'

    if include_meta == 'only':
        print(json.dumps({{ 'meta': meta }}, indent=2))

    else:
        for result in pgmapcss_{style_id}(bounds, scale_denom, parameters):
            if result['object'] == last_object:
                results.append(result)

            else:
                if len(results) == 0:
                    print('{{')
                    if include_meta == 'true':
                        print('  "meta": ', end='')
                        print(json.dumps(meta, indent=2).replace('\n', '\n  '), end='')
                        print(',')
                    print('  "type": "FeatureCollection",')
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

    plpy.execute(plpy.prepare('truncate _pgmapcss_PGCache', []), [])
    plpy.execute(plpy.prepare('commit', []), [])
