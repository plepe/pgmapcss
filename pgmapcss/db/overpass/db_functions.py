#[out:json][bbox:{{bbox}}];(way[name=Marschnergasse];way[name=Erdbrustgasse]);out geom meta;

def overpass_query(query):
    import urllib.request
    import urllib.parse
    import json

# START debug.overpass_queries
    plpy.warning(query)
# END debug.overpass_queries
# START debug.profiler
    ret = []
    time_start = datetime.datetime.now()
# END debug.profiler
    url = '{db.overpass-url}/interpreter?' +\
        urllib.parse.urlencode({ 'data': query })

    f = urllib.request.urlopen(url)

    block = ''
    mode = 0
    while True:
        r = f.readline().decode('utf-8')
        if r == '':
            raise Exception('Connection closed early from Overpass API')

        if mode == 0:
            if re.search('"elements":', r):
                mode = 1

            # areas not initialized -> ignore
            if re.search('osm3s_v[0-9\.]+_areas', r):
                f.close()
                return

        elif mode == 1:
            if re.match('}', r):
                block += '}'
# START debug.profiler
                ret.append(json.loads(block))
# ELSE debug.profiler
                yield json.loads(block)
# END debug.profiler

                block = ''

            elif re.match('\s*$', block) and re.match('.*\]', r):
                f.close()

# START debug.profiler
                plpy.warning('%s\nquery took %.2fs for %d features' % (query, (datetime.datetime.now() - time_start).total_seconds(), len(ret)))
                for r in ret:
                    yield r
# END debug.profiler

                return

            else:
                block += r

    if mode == 0:
        raise Exception('Could not parse Overpass API result')

def node_geom(lat, lon):
    global geom_plan

    try:
        geom_plan
    except NameError:
        geom_plan = plpy.prepare('select ST_GeomFromText($1, 4326) as geom', [ 'text' ])

    res = plpy.execute(geom_plan, [ 'POINT({} {})'.format(lon, lat) ])

    return res[0]['geom']

def way_geom(r, is_polygon):
    global geom_plan

    try:
        geom_plan
    except NameError:
        geom_plan = plpy.prepare('select ST_GeomFromText($1, 4326) as geom', [ 'text' ])

    geom_str = ','.join([
        str(p['lon']) + ' ' + str(p['lat'])
        for p in r['geometry']
    ])

    if is_polygon:
        geom_str = 'POLYGON((' + geom_str + '))'
    else:
        geom_str = 'LINESTRING('+ geom_str + ')'

    res = plpy.execute(geom_plan, [ geom_str ])

    return res[0]['geom']

def linestring(geom):
    return 'LINESTRING(' + ','.join([
                '{} {}'.format(g['lon'], g['lat'])
                for g in geom
            ]) + ')'

def multipolygon_geom(r):
    global geom_plan

    try:
        geom_plan_makepoly
    except NameError:
        geom_plan_makepoly = plpy.prepare('select ST_SetSRID(ST_MakePolygon(ST_GeomFromText($1)), 4326) as geom', [ 'text' ])
        geom_plan_collect = plpy.prepare('select ST_Collect($1) as geom', [ 'geometry[]' ])
        geom_plan_substract = plpy.prepare('select ST_Difference($1, $2) as geom', [ 'geometry', 'geometry' ])
        # merge all lines together, return all closed rings (but remove unconnected lines)
        geom_plan_linemerge = plpy.prepare('select geom from (select (ST_Dump((ST_LineMerge(ST_Collect(geom))))).geom as geom from (select ST_GeomFromText(unnest($1), 4326) geom) t offset 0) t where ST_NPoints(geom) > 3 and ST_IsClosed(geom)', [ 'text[]' ])

    t = 'MULTIPOLYGON'

    polygons = []
    lines = []
    inner_polygons = []
    inner_lines = []

    for m in r['members']:
        if not 'geometry' in m:
          continue

        if m['role'] in ('outer', ''):
            if len(m['geometry']) > 3 and m['geometry'][0] == m['geometry'][-1]:
                polygons.append(linestring(m['geometry']))
            else:
                lines.append(linestring(m['geometry']))

        elif m['role'] in ('inner'):
            if len(m['geometry']) > 3 and m['geometry'][0] == m['geometry'][-1]:
                inner_polygons.append(linestring(m['geometry']))
            else:
                inner_lines.append(linestring(m['geometry']))

    polygons = [
            plpy.execute(geom_plan_makepoly, [ p ])[0]['geom']
            for p in polygons
        ]

    lines = plpy.execute(geom_plan_linemerge, [ lines ])
    for p in lines:
        polygons.append(p['geom'])

    polygons = plpy.execute(geom_plan_collect, [ polygons ])[0]['geom']
    inner_polygons = [
            plpy.execute(geom_plan_makepoly, [ p ])[0]['geom']
            for p in inner_polygons
        ]

    inner_lines = plpy.execute(geom_plan_linemerge, [ inner_lines ])
    for p in inner_lines:
        inner_polygons.append(p['geom'])

    for p in inner_polygons:
        try:
            polygons = plpy.execute(geom_plan_substract, [ polygons, p ])[0]['geom']
        except:
            plpy.warning('DB/Overpass::relation_geom({}): error substracting inner polygons'.format(r['id']))
            pass

    inner_polygons = None

    return polygons

def relation_geom(r):
    global geom_plan_collect

    try:
        geom_plan_collect
    except NameError:
        geom_plan_collect = plpy.prepare('select ST_Collect($1) as geom', [ 'geometry[]' ])

    l = []

    for m in r['members']:
        if m['type'] == 'node':
            l.append(node_geom(m['lat'], m['lon']))
        if m['type'] == 'way':
            l.append(way_geom(m, None))

    res = plpy.execute(geom_plan_collect, [ l ])

    return res[0]['geom']

def assemble_object(r, way_polygon=None):
    t = {
        'tags': r['tags'] if 'tags' in r else {},
    }
    if r['type'] == 'node':
        t['id'] = 'n' + str(r['id'])
        t['types'] = ['node', 'point']
        t['geo'] = node_geom(r['lat'], r['lon'])
    elif r['type'] == 'way':
        is_polygon = way_polygon in (True, None) and len(r['nodes']) > 3 and r['nodes'][0] == r['nodes'][-1]
        if way_polygon is True and not is_polygon:
            return None
        t['id'] = 'w' + str(r['id'])
        t['types'] = ['way']
        if is_polygon:
            t['types'].append('area')
        else:
            t['types'].append('line')
        t['geo'] = way_geom(r, is_polygon)
        t['members'] = [
                {
                    'member_id': 'n' + str(m),
                    'sequence_id': str(i),
                }
                for i, m in enumerate(r['nodes'])
            ]
    elif r['type'] == 'relation':
        t['id'] = 'r' + str(r['id'])
        t['types'] = ['area', 'relation']
        if 'tags' in r and 'type' in r['tags'] and r['tags']['type'] in ('multipolygon', 'boundary'):
            t['geo'] = multipolygon_geom(r)
        else:
            t['geo'] = relation_geom(r)
        t['members'] = [
                {
                    'member_id': m['type'][0] + str(m['ref']),
                    'role': m['role'],
                    'sequence_id': str(i),
                }
                for i, m in enumerate(r['members'])
            ]
    t['tags']['osm:id'] = t['id']
    t['tags']['osm:version'] = str(r['version']) if 'version' in r else ''
    t['tags']['osm:user_id'] = str(r['uid']) if 'uid' in r else ''
    t['tags']['osm:user'] = r['user'] if 'user' in r else ''
    t['tags']['osm:timestamp'] = r['timestamp'] if 'timestamp' in r else ''
    t['tags']['osm:changeset'] = str(r['changeset']) if 'changeset' in r else ''

    return t

def get_bbox(_bbox=None):
    if _bbox is None:
        _bbox = render_context['bbox']

    plan = plpy.prepare("select ST_YMin($1::geometry) || ',' || ST_XMIN($1::geometry) || ',' || ST_YMAX($1::geometry) || ',' || ST_XMAX($1::geometry) as bbox_string", [ 'geometry' ])
    res = plpy.execute(plan, [ _bbox ])
    return res[0]['bbox_string']

def objects(_bbox, where_clauses, add_columns={}, add_param_type=[], add_param_value=[]):
    time_start = datetime.datetime.now() # profiling
    non_relevant_tags = {'type', 'source', 'source:ref', 'source_ref', 'note', 'comment', 'created_by', 'converted_by', 'fixme', 'FIXME', 'description', 'attribution', 'osm:id', 'osm:version', 'osm:user_id', 'osm:user', 'osm:timestamp', 'osm:changeset'}
    ways_done = []
    rels_done = []
    area_ways_done = []

    qry = '[out:json]'
    replacements = {}

    if _bbox:
        qry += '[bbox:' + get_bbox(_bbox) + ']'
        replacements['__BBOX__'] = '(' + get_bbox(_bbox) + ')'
    else:
        replacements['__BBOX__'] = ''

    qry += ';__QRY__;out meta geom;'

    # nodes
    w = []
    for t in ('*', 'node', 'point'):
        if t in where_clauses:
            w.append(where_clauses[t])

    if len(w):
        parent_query = ''
        for w1 in w:
            if 'parent_query' in w1:
                parent_query += w1['parent_query']

        q = qry.replace('__QRY__', parent_query + '((' + ');('.join([ w1['query'] for w1 in w ]) + ');)')
        q = q.replace('__TYPE__', 'node')
        for r1, r2 in replacements.items():
            q = q.replace(r1, r2)

        for r in overpass_query(q):
            yield(assemble_object(r))

        #'http://overpass-turbo.eu/?Q=' + q).read()

    # way areas and multipolygons based on outer tags
    w = []
    for t in ('*', 'area'):
        if t in where_clauses:
            w.append(where_clauses[t])

    if len(w):
        # query for ways which match query, also get their parent relations and
        # again all child ways. if a way is outer way of a multipolygon, the
        # multipolygon has no (relevant) tags and all outer ways share the same
        # tags (save non relevant tags) the ways are discarded and the relation
        # is used - as type 'multipolygon' and a 'm' prefixed to the ID
        parent_query = ''
        for w1 in w:
            if 'parent_query' in w1:
                parent_query += w1['parent_query']

        q1 = ');('.join([ w1['query'] for w1 in w ]).replace('__TYPE__', 'way(r.rel:"outer")')
        q2 = ');('.join([ w1['query'] for w1 in w ]).replace('__TYPE__', 'way(r.rel:"")')

        q = qry.replace('__QRY__', parent_query +\
                "relation[type~'^multipolygon|boundary$'] -> .rel;" +
                '((' + q1 + q2 + ");) -> .outer;relation(bw.outer)[type~'^multipolygon|boundary$']") + '.outer out tags qt;'

        _ways = {}
        _rels = {}

        for r in overpass_query(q):
            if r['type'] == 'way':
                _ways[r['id']] = r
            elif r['type'] == 'relation':
                _rels[r['id']] = r

        for rid, r in _rels.items():
            mp_tags = {
                    vk: vv
                    for vk, vv in r['tags'].items()
                    if vk not in non_relevant_tags
                }
            is_valid_mp = True
            outer_tags = None

            for outer in r['members']:
                if outer['role'] in ('', 'outer'):
                    if not outer['ref'] in _ways:
                        continue

                    outer_way = _ways[outer['ref']]
                    tags = {
                            vk: vv
                            for vk, vv in outer_way['tags'].items()
                            if vk not in non_relevant_tags
                        } if 'tags' in outer_way else {}

                    if outer_tags is None:
                        outer_tags = tags
                    elif outer_tags != tags:
                        is_valid_mp = True

            if (len(mp_tags) == 0 or mp_tags == outer_tags) and \
                is_valid_mp and outer_tags is not None:
                rels_done.append(rid)
                for outer in r['members']:
                    if outer['role'] in ('', 'outer'):
                        area_ways_done.append(outer['ref'])

                t = assemble_object(r)
                if len(mp_tags) == 0:
                    t['id'] = 'm' + str(r['id'])
                    t['types'] = ['multipolygon', 'area']
                    t['tags'] = outer_tags
                    t['tags']['osm:id'] = t['id']
                    t['tags']['osm:has_outer_tags'] = 'yes'

                yield(t)

        _ways = None
        _rels = None

    # ways - will be run 3 times, first for areas, then lines and finally for not specified ways
    for types in [
            { 'types': ('area',), 'way_polygon': True },
            { 'types': ('line',), 'way_polygon': False },
            { 'types': ('*', 'way'), 'way_polygon': None },
        ]:
        w = []
        for t in types['types']:
            if t in where_clauses:
                w.append(where_clauses[t])

        if len(w):
            parent_query = ''
            for w1 in w:
                if 'parent_query' in w1:
                    parent_query += w1['parent_query']

            q = qry.replace('__QRY__', parent_query + '((' + ');('.join([ w1['query'] for w1 in w ]) + ');)')
            q = q.replace('__TYPE__', 'way')
            for r1, r2 in replacements.items():
                q = q.replace(r1, r2)

            for r in overpass_query(q):
                if r['id'] in ways_done:
                    continue

                # check, if way was part of multipolygon (with tags from outer
                # ways) -> may not be area
                way_polygon = types['way_polygon']
                if r['id'] in area_ways_done:
                    if types['way_polygon'] == True:
                        continue
                    else:
                        way_polygon = False

                t = assemble_object(r, way_polygon=way_polygon)
                if t:
                    ways_done.append(r['id'])
                    yield t

    # relations
    w = []
    parent_query = ''
    for t, type_condition in {'*': '', 'relation': '', 'area': "[type~'^multipolygon|boundary$']"}.items():
        if t in where_clauses:
            w.append(where_clauses[t]['query'].replace('__TYPE__', 'relation' + type_condition))
            if 'parent_query' in where_clauses[t]:
                parent_query += where_clauses[t]['parent_query']

    if len(w):
        q = qry.replace('__QRY__', parent_query + '((' + ');('.join(w) + ');)')
        for r1, r2 in replacements.items():
            q = q.replace(r1, r2)

        for r in overpass_query(q):
            if r['id'] in rels_done:
                continue
            rels_done.append(r['id'])

            yield(assemble_object(r))

    # areas
    w = []
    for t in ('*', 'area'):
        if t in where_clauses:
            w.append(where_clauses[t])

    if len(w):
        plan = plpy.prepare("select ST_Y(ST_Centroid($1::geometry)) || ',' || ST_X(ST_Centroid($1::geometry)) as geom", [ 'geometry' ])
        res = plpy.execute(plan, [ _bbox ])

        q1 = ');('.join([ w1['query'] for w1 in w ]).replace('__TYPE__', 'relation(pivot.a)')
        q2 = ');('.join([ w1['query'] for w1 in w ]).replace('__TYPE__', 'way(pivot.a)')

        q = ('[out:json];is_in({})->.a;(' + q1 + q2 + ');out meta geom;').format(res[0]['geom'])
        for r1, r2 in replacements.items():
            q = q.replace(r1, r2)

        for r in overpass_query(q):
            if (r['type'] == 'way' and r['id'] in ways_done) or\
               (r['type'] == 'relation' and r['id'] in rels_done):
                continue

            yield(assemble_object(r))

    time_stop = datetime.datetime.now() # profiling
    plpy.notice('querying db objects took %.2fs' % (time_stop - time_start).total_seconds())

def objects_by_id(objects):
    q = ''
    multipolygons = []
    for o in objects:
        i = o['id']

        if i[0:1] == 'n':
            q += 'node({});out meta geom;'.format(i[1:])
        elif i[0:1] == 'w':
            q += 'way({});out meta geom;'.format(i[1:])
        elif i[0:1] == 'r':
            q += 'relation({});out meta geom;'.format(i[1:])

    if q == '':
        return
    q = '[out:json];' + q

    for r in overpass_query(q):
        yield(assemble_object(r))

def objects_member_of(objects, args):
    q = '[out:json][bbox:' + get_bbox() + '];'
    q += '(' + args['child_conditions']['parent_query'] + ');'
    q += 'out meta qt geom;'

    for r in overpass_query(q):
        t = assemble_object(r)

        for o in objects:
            for m in t['members']:
                if o['id'] == m['member_id']:
                    link_tags = {
                            'sequence_id': m['sequence_id'],
                            'member_id': m['member_id'],
                        }
                    if 'role' in m:
                        link_tags['role'] = m['role']

                    yield (o, t, link_tags)

def objects_members(objects, args):
    q_list = '';
    types = set()

    for o in objects:
        member_id = o['id']

        if member_id[0] == 'w':
            q_list += 'way(' + member_id[1:] + ');'
            types.add('w')
        elif member_id[0] == 'r':
            q_list += 'relation(' + member_id[1:] + ');'
            types.add('r')

    q = '[out:json];(' + q_list + ')->.a;'
    q += '('

    for t in types:
        q += args['parent_conditions']['query'].replace('__TYPE__', args['parent_type'] + '(' + t + '.a)(' + get_bbox() + ')')

    q += ');out meta qt geom;'

    for r in overpass_query(q):
        t = assemble_object(r)

        for o in objects:
            for m in o['members']:
                if t['id'] == m['member_id']:
                    link_tags = {
                            'sequence_id': m['sequence_id'],
                            'member_id': m['member_id'],
                        }
                    if 'role' in m:
                        link_tags['role'] = m['role']

                    yield (o, t, link_tags)

def objects_near(objects_list, args):
    cache_id = 'objects_near' + '|' + args['parent_type'] + '|' + repr(args['parent_conditions'])

    max_distance = to_float(eval_metric([ args['distance'], 'u' ], None))
    if max_distance is None:
        return

    try:
        cache = get_PGCache(cache_id)
    except:
        cache = PGCache(cache_id, read_geo=True)

        plan = plpy.prepare('select ST_Transform(ST_Envelope(ST_Buffer(ST_Transform(ST_Envelope($1::geometry), {unit.srs}), $2)), {db.srs}) as r', ['geometry', 'float'])
        res = plpy.execute(plan, [ render_context['bbox'], max_distance ])
        bbox = res[0]['r']

        for t in objects(bbox, { args['parent_type']: args['parent_conditions'] }):
            cache.add(t)

    for ob in objects_list:
        if ob:
            geom = ob['geo']
        elif 'geo' in current['properties'][current['pseudo_element']]:
            geom = current['properties'][current['pseudo_element']]['geo']
        else:
            geom = current['object']['geo']

        if max_distance == 0:
            bbox = geom
        else:
            plan = plpy.prepare('select ST_Transform(ST_Buffer(ST_Transform(ST_Envelope($1), {unit.srs}), $2), {db.srs}) as r', ['geometry', 'float'])
            res = plpy.execute(plan, [ geom, max_distance ])
            bbox = res[0]['r']

        if not 'check_geo' in args:
            pass
        elif args['check_geo'] == 'within':
            where_clause += " and ST_DWithin(geo, $1, 0.0)"
        elif args['check_geo'] == 'surrounds':
            where_clause += " and ST_DWithin($1, geo, 0.0)"
        elif args['check_geo'] == 'overlaps':
            where_clause += " and ST_Overlaps($1, geo)"

        plan = cache.prepare('select * from (select *, ST_Distance(ST_Transform($1, {unit.srs}), ST_Transform(geo, {unit.srs})) dist from {table} where geo && $2 offset 0) t order by dist asc', [ 'geometry', 'geometry' ])
        for t in cache.cursor(plan, [ geom, bbox ]):
            o = t['data']

            if o['id'] != ob['id'] and t['dist'] <= max_distance:
                link_tags = {
                    'distance': eval_metric([ str(t['dist']) + 'u', 'px' ], o)
                }

                yield ( ob, o, link_tags )
