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

    first = True
    for result in pgmapcss_{style_id}(bounds, scale_denom):
        if first:
            print('{{ "type": "FeatureCollection", "features": [')
            first = False
        else:
            print(",")

        res = plpy.execute(plan_to_geojson, [ result['geo'] ])

        tags = dict(result['tags'])
        tags['result'] = result['properties']
        feature = {{
            'type': 'Feature',
            'geometry': json.loads(res[0]['r']) if res[0]['r'] else None,
            'properties': tags,
        }}

        print(json.dumps(feature, indent=2))

    if first:
        print('{{ "type": "FeatureCollection", "features": []}}')
    else:
        print("]}}\n")
