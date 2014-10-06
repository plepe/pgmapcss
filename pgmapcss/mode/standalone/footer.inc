if __name__ == '__main__':
    import argparse
    import re
    import json

    # Handle negative values in --bounds parameter
    # thanks to http://stackoverflow.com/a/21446783
    for i, arg in enumerate(sys.argv):
        if (arg[0] == '-') and arg[1].isdigit(): sys.argv[i] = ' ' + arg

    parser = argparse.ArgumentParser(description='Executes the compiled map style and prints resulting objects.')

    parser.add_argument('-b', '--bounds', dest='bounds',
        help='Process the map from the specified bounding box as min_lon,min_lat,max_lon,max_lat in WGS-84. (default: whole database)'
    )

    parser.add_argument('-s', '--scale', dest='scale',
        default='2000',
        help='Process map at a specified scale denominator. If z<zoom> syntax (e.g. "z15") is used, the zoom levels of projection 900913 are used.'
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

    plpy = fake_plpy()
    plan_to_geojson = plpy.prepare('select ST_asGeoJSON(ST_Transform($1, 4326)) as r', [ 'geometry' ])

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

    parameters = {{ }}

    for result in pgmapcss_{style_id}(bounds, scale_denom, parameters):
        if result['object'] == last_object:
            results.append(result)

        else:
            if len(results) == 0:
                print('{{ "type": "FeatureCollection", "features": [')
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
