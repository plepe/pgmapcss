#[out:json][bbox:{{bbox}}];(way[name=Marschnergasse];way[name=Erdbrustgasse]);out geom meta;

def overpass_query(query):
    import urllib.request
    import urllib.parse
    import json

    plpy.warning(query)
    url = '{db.overpass-url}?' +\
        urllib.parse.urlencode({ 'data': query })
    f = urllib.request.urlopen(url).read().decode('utf-8')

    try:
        res = json.loads(f)
    except ValueError:
        # areas not initialized -> ignore
        if re.search('osm3s_v[0-9\.]+_areas', f):
            return
        else:
            raise

    for r in res['elements']:
        yield(r)

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

def relation_geom(r):
    global geom_plan

    try:
        geom_plan_makepoly
    except NameError:
        geom_plan_makepoly = plpy.prepare('select ST_SetSRID(ST_MakePolygon(ST_GeomFromText($1)), 4326) as geom', [ 'text' ])
        geom_plan_collect = plpy.prepare('select ST_Collect($1) as geom', [ 'geometry[]' ])
        geom_plan_substract = plpy.prepare('select ST_Difference($1, $2) as geom', [ 'geometry', 'geometry' ])
        # merge all lines together, return all closed rings (but remove unconnected lines)
        geom_plan_linemerge = plpy.prepare('select geom from (select (ST_Dump((ST_LineMerge(ST_Collect(geom))))).geom as geom from (select ST_GeomFromText(unnest($1), 4326) geom) t offset 0) t where ST_NPoints(geom) > 3 and ST_IsClosed(geom)', [ 'text[]' ])

    if 'tags' in r and 'type' in r['tags'] and r['tags']['type'] in ('multipolygon', 'boundary'):
        t = 'MULTIPOLYGON'
    else:
        return None

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
    for r in lines:
        polygons.append(r['geom'])

    polygons = plpy.execute(geom_plan_collect, [ polygons ])[0]['geom']
    inner_polygons = [
            plpy.execute(geom_plan_makepoly, [ p ])[0]['geom']
            for p in inner_polygons
        ]

    inner_lines = plpy.execute(geom_plan_linemerge, [ inner_lines ])
    for r in inner_lines:
        inner_polygons.append(r['geom'])

    for p in inner_polygons:
        try:
            polygons = plpy.execute(geom_plan_substract, [ polygons, p ])[0]['geom']
        except:
            plpy.warning('DB/Overpass::relation_geom({}): error substracting inner polygons'.format(r['id']))
            pass

    inner_polygons = None

    return polygons

def assemble_object(r):
    t = {
        'tags': r['tags'] if 'tags' in r else {},
    }
    if r['type'] == 'node':
        t['id'] = 'n' + str(r['id'])
        t['types'] = ['node', 'point']
        t['geo'] = node_geom(r['lat'], r['lon'])
    elif r['type'] == 'way':
        is_polygon = len(r['nodes']) > 3 and r['nodes'][0] == r['nodes'][-1]
        t['id'] = 'w' + str(r['id'])
        t['types'] = ['line', 'way']
        if is_polygon:
            t['types'].append('area')
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
    return '[bbox:' + res[0]['bbox_string'] + ']'

def objects(_bbox, where_clauses, add_columns={}, add_param_type=[], add_param_value=[]):
    time_start = datetime.datetime.now() # profiling
    non_relevant_tags = {'type', 'source', 'source:ref', 'source_ref', 'note', 'comment', 'created_by', 'converted_by', 'fixme', 'FIXME', 'description', 'attribution', 'osm:id', 'osm:version', 'osm:user_id', 'osm:user', 'osm:timestamp', 'osm:changeset'}
    ways_done = []
    rels_done = []

    qry = '[out:json]'

    if _bbox:
        qry += get_bbox(_bbox)

    qry += ';__QRY__;out meta geom;'

    # nodes
    w = []
    for t in ('*', 'node', 'point'):
        if t in where_clauses:
            w.append(where_clauses[t])

    if len(w):
        q = qry.replace('__QRY__', '((' + ');('.join(w) + ');)')
        q = q.replace('__TYPE__', 'node')

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
        q1 = ');('.join(w).replace('__TYPE__', 'way(r.rel:"outer")')
        q2 = ');('.join(w).replace('__TYPE__', 'way(r.rel:"")')

        q = qry.replace('__QRY__',
                'relation[type=multipolygon] -> .rel;' +
                '((' + q1 + q2 + ');) -> .outer;relation(bw.outer)[type=multipolygon]') + '.outer out tags qt;'

        _ways = {}
        _rels = {}

        for r in overpass_query(q):
            if r['type'] == 'way':
                _ways[r['id']] = r
            elif r['type'] == 'relation':
                _rels[r['id']] = r

        for rid, r in _rels.items():
            if r['tags']['type'] in ('multipolygon', 'boundary') and len([
                    v
                    for v in r['tags']
                    if v not in non_relevant_tags
                ]) == 0:
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

                if is_valid_mp and outer_tags is not None:
                    rels_done.append(rid)
                    for outer in r['members']:
                        if outer['role'] in ('', 'outer'):
                            ways_done.append(outer['ref'])

                    t = assemble_object(r)
                    t['id'] = 'm' + str(r['id'])
                    t['types'] = ['multipolygon', 'area']
                    t['tags'] = outer_tags

                    yield(t)
                else:
                    plpy.warning('tag-less multipolygon with non-similar outer ways: {}'.format(rid))

        _ways = None
        _rels = None

    # ways
    w = []
    for t in ('*', 'line', 'way', 'area'):
        if t in where_clauses:
            w.append(where_clauses[t])

    if len(w):
        q = qry.replace('__QRY__', '((' + ');('.join(w) + ');)')
        q = q.replace('__TYPE__', 'way')

        for r in overpass_query(q):
            if r['id'] in ways_done:
                pass
            ways_done.append(r['id'])

            yield(assemble_object(r))

    # relations
    w = []
    for t in ('*', 'relation', 'area'):
        if t in where_clauses:
            w.append(where_clauses[t])

    if len(w):
        q = qry.replace('__QRY__', '((' + ');('.join(w) + ');)')
        q = q.replace('__TYPE__', 'relation')

        for r in overpass_query(q):
            if r['id'] in rels_done:
                pass
            rels_done.append(r['id'])

            yield(assemble_object(r))

    # areas
    w = []
    for t in ('*', 'relation', 'area'):
        if t in where_clauses:
            w.append(where_clauses[t])

    if len(w):
        plan = plpy.prepare("select ST_Y(ST_Centroid($1::geometry)) || ',' || ST_X(ST_Centroid($1::geometry)) as geom", [ 'geometry' ])
        res = plpy.execute(plan, [ _bbox ])

        q = qry.replace('__QRY__', 'is_in({0});way(pivot);out meta geom;is_in({0});relation(pivot)'.format(res[0]['geom']))

        for r in overpass_query(q):
            if (r['type'] == 'way' and r['id'] in ways_done) or\
               (r['type'] == 'relation' and r['id'] in rels_done):
                continue

            yield(assemble_object(r))

    time_stop = datetime.datetime.now() # profiling
    plpy.notice('querying db objects took %.2fs' % (time_stop - time_start).total_seconds())

def objects_by_id(id_list):
    q = ''
    multipolygons = []
    for i in id_list:
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

def objects_member_of(member_id, parent_type, parent_conditions, child_conditions):
    global member_of_cache
    try:
        member_of_cache
    except:
        member_of_cache = {}

    if member_id[0] == 'n':
        ob_type = 'node'
        ob_id = int(member_id[1:])
    elif member_id[0] == 'w':
        ob_type = 'way'
        ob_id = int(member_id[1:])
    elif member_id[0] == 'r':
        ob_type = 'relation'
        ob_id = int(member_id[1:])

    member_of_cache_id = parent_type + '|' + ob_type + '|' + repr(parent_conditions) + '|' + repr(child_conditions)

    if member_of_cache_id not in member_of_cache:
        member_of_cache[member_of_cache_id] = []
        q = '[out:json]' + get_bbox() + ';'

        q += '(' + child_conditions.replace('__TYPE__', ob_type) + ')->.a;'

        q += '(' + parent_conditions.replace('__TYPE__', parent_type + '(b' +
                ob_type[0] + '.a)') + ');'
        q += 'out meta qt geom;'

        for r in overpass_query(q):
            t = assemble_object(r)
            member_of_cache[member_of_cache_id].append(t)

    for t in member_of_cache[member_of_cache_id]:
        for m in t['members']:
            if m['member_id'] == member_id:
                t['link_tags'] = {
                        'sequence_id': m['sequence_id'],
                        'member_id': m['member_id'],
                }
                if 'role' in m:
                    t['link_tags']['role'] = m['role']

                yield(t)

def objects_members(relation_id, parent_type, parent_conditions, child_conditions):
    global members_cache
    try:
        members_cache
    except:
        members_cache = {}

    q = '[out:json];'

    if relation_id[0] == 'n':
        ob_type = 'node'
        ob_id = int(relation_id[1:])
    elif relation_id[0] == 'w':
        ob_type = 'way'
        ob_id = int(relation_id[1:])
    elif relation_id[0] == 'r':
        ob_type = 'relation'
        ob_id = int(relation_id[1:])

    members_cache_id = parent_type + '|' + ob_type + '|' + repr(parent_conditions) + '|' + repr(child_conditions)

    if members_cache_id not in members_cache:
        members_cache[members_cache_id] = { 'parents': {}, 'children': [] }
        q = '[out:json]' + get_bbox() + ';'

        q += '(' + child_conditions.replace('__TYPE__', ob_type) + ');'
        q += 'out meta qt geom;'
        # TODO: out body qt; would be sufficient, but need to adapt assemble_object

        for r in overpass_query(q):
            t = assemble_object(r)
            t['type'] = r['type']
            members_cache[members_cache_id]['parents'][t['id']] = t

        q = '[out:json]' + get_bbox() + ';'

        q += '(' + child_conditions.replace('__TYPE__', ob_type) + ')->.a;'
        q += '(' + parent_conditions.replace('__TYPE__', parent_type + '(' +
                relation_id[0] + '.a)') + ');'
        q += 'out meta qt geom;'
        # TODO: .a out body qt; would be sufficient, but need to adapt assemble_object

        for r in overpass_query(q):
            t = assemble_object(r)
            members_cache[members_cache_id]['children'].append(t)

    relation = members_cache[members_cache_id]['parents'][relation_id]

    for t in members_cache[members_cache_id]['children']:
        for m in relation['members']:
            if m['member_id'] == t['id']:
                t['link_tags'] = {
                        'sequence_id': m['sequence_id'],
                        'member_id': m['member_id'],
                }
                if 'role' in m:
                    t['link_tags']['role'] = m['role']

                yield(t)

def objects_near(max_distance, ob, parent_type, parent_conditions, child_conditions, check_geo=None):
    cache_id = 'objects_near' + '|' + parent_type + '|' + repr(parent_conditions)

    max_distance = to_float(eval_metric([ max_distance, 'u' ]))
    if max_distance is None:
        return

    try:
        cache = get_PGCache(cache_id)
    except:
        cache = PGCache(cache_id, read_geo=True)

        plan = plpy.prepare('select ST_Transform(ST_Envelope(ST_Buffer(ST_Transform(ST_Envelope($1::geometry), {unit.srs}), $2)), {db.srs}) as r', ['geometry', 'float'])
        res = plpy.execute(plan, [ render_context['bbox'], max_distance ])
        bbox = res[0]['r']

        for t in objects(bbox, { parent_type: parent_conditions }):
            cache.add(t)

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

    if check_geo == 'within':
        where_clause += " and ST_DWithin(geo, $1, 0.0)"
    elif check_geo == 'surrounds':
        where_clause += " and ST_DWithin($1, geo, 0.0)"
    elif check_geo == 'overlaps':
        where_clause += " and ST_Overlaps($1, geo)"

    plan = cache.prepare('select * from (select *, ST_Distance(ST_Transform($1, {unit.srs}), ST_Transform(geo, {unit.srs})) dist from {table} where geo && $2 offset 0) t order by dist asc', [ 'geometry', 'geometry' ])
    for t in cache.cursor(plan, [ geom, bbox ]):
        ob = t['data']

        if ob['id'] != current['object']['id'] and t['dist'] <= max_distance:
            ob['link_tags'] = {
                'distance': eval_metric([ str(t['dist']) + 'u', 'px' ])
            }

            yield ob
