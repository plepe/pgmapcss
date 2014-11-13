#[out:json][bbox:{{bbox}}];(way[name=Marschnergasse];way[name=Erdbrustgasse]);out geom meta;

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
        if m['role'] in ('outer', ''):
            if m['geometry'][0] == m['geometry'][-1]:
                polygons.append(linestring(m['geometry']))
            else:
                lines.append(linestring(m['geometry']))

        elif m['role'] in ('inner'):
            if m['geometry'][0] == m['geometry'][-1]:
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
        polygons = plpy.execute(geom_plan_substract, [ polygons, p ])[0]['geom']
    inner_polygons = None

    return polygons

def objects(_bbox, where_clauses, add_columns={}, add_param_type=[], add_param_value=[]):
    import urllib.request
    import urllib.parse
    import json
    time_start = datetime.datetime.now() # profiling
    non_relevant_tags = {'type', 'source', 'source:ref', 'source_ref', 'note', 'comment', 'created_by', 'converted_by', 'fixme', 'FIXME', 'description', 'attribution', 'osm:id', 'osm:version', 'osm:user_id', 'osm:user', 'osm:timestamp', 'osm:changeset'}
    ways_done = []
    rels_done = []

    qry = '[out:json]'

    if _bbox:
        plan = plpy.prepare("select ST_YMin($1::geometry) || ',' || ST_XMIN($1::geometry) || ',' || ST_YMAX($1::geometry) || ',' || ST_XMAX($1::geometry) as bbox_string", [ 'geometry' ])
        res = plpy.execute(plan, [ _bbox ])
        qry += '[bbox:' + res[0]['bbox_string'] + ']'

    qry += ';__QRY__;out meta geom;'

    # nodes
    w = []
    for t in ('*', 'node', 'point'):
        if t in where_clauses:
            w.append(where_clauses[t])

    if len(w):
        q = qry.replace('__QRY__', '((' + ');('.join(w) + ');)')
        q = q.replace('__TYPE__', 'node')

        url = 'http://overpass-api.de/api/interpreter?' +\
            urllib.parse.urlencode({ 'data': q })
        f = urllib.request.urlopen(url).read().decode('utf-8')
        res = json.loads(f)

        for r in res['elements']:
            t = {
                'id': 'n' + str(r['id']),
                'types': ['node', 'point'],
                'tags': r['tags'],
                'geo': node_geom(r['lat'], r['lon']),
            }
            t['tags']['osm:id'] = t['id']
            t['tags']['osm:version'] = str(r['version']) if 'version' in r else ''
            t['tags']['osm:user_id'] = str(r['uid']) if 'uid' in r else ''
            t['tags']['osm:user'] = r['user'] if 'user' in r else ''
            t['tags']['osm:timestamp'] = r['timestamp'] if 'timestamp' in r else ''
            t['tags']['osm:changeset'] = str(r['changeset']) if 'changeset' in r else ''
            yield(t)

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
        q = qry.replace('__QRY__',
                'relation[type=multipolygon] -> .rel;' +
                '((' + ');('.join(w) + ');) -> .outer;relation(bw.outer)[type=multipolygon]') + '.outer out tags qt;'
        q = q.replace('__TYPE__', 'way(r.rel:"outer")')
        plpy.warning(q)

        url = 'http://overpass-api.de/api/interpreter?' +\
            urllib.parse.urlencode({ 'data': q })
        f = urllib.request.urlopen(url).read().decode('utf-8')
        res = json.loads(f)

        _ways = {}
        _rels = {}

        for r in res['elements']:
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

                if is_valid_mp:
                    rels_done.append(rid)
                    for outer in r['members']:
                        if outer['role'] in ('', 'outer'):
                            ways_done.append(outer['ref'])

                    t = {
                        'id': 'm' + str(r['id']),
                        'types': ['multipolygon', 'area'],
                        # TODO: merge tags with relation tags and
                        # (non-relevant) tags of other outer ways
                        'tags': outer_tags,
                        'geo': relation_geom(r),
                    }
                    t['tags']['osm:id'] = t['id']
                    t['tags']['osm:version'] = str(r['version']) if 'version' in r else ''
                    t['tags']['osm:user_id'] = str(r['uid']) if 'uid' in r else ''
                    t['tags']['osm:user'] = r['user'] if 'user' in r else ''
                    t['tags']['osm:timestamp'] = r['timestamp'] if 'timestamp' in r else ''
                    t['tags']['osm:changeset'] = str(r['changeset']) if 'changeset' in r else ''

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
        plpy.warning(q)

        url = 'http://overpass-api.de/api/interpreter?' +\
            urllib.parse.urlencode({ 'data': q })
        f = urllib.request.urlopen(url).read().decode('utf-8')
        res = json.loads(f)

        for r in res['elements']:
            if r['id'] in ways_done:
                pass
            ways_done.append(r['id'])

            is_polygon = len(r['nodes']) > 3 and r['nodes'][0] == r['nodes'][-1]
            t = {
                'id': 'w' + str(r['id']),
                'types': ['way', 'line', 'area'] if is_polygon else ['way', 'line'],
                'tags': r['tags'] if 'tags' in r else {},
                'geo': way_geom(r, is_polygon),
            }
            t['tags']['osm:id'] = t['id']
            t['tags']['osm:version'] = str(r['version']) if 'version' in r else ''
            t['tags']['osm:user_id'] = str(r['uid']) if 'uid' in r else ''
            t['tags']['osm:user'] = r['user'] if 'user' in r else ''
            t['tags']['osm:timestamp'] = r['timestamp'] if 'timestamp' in r else ''
            t['tags']['osm:changeset'] = str(r['changeset']) if 'changeset' in r else ''

            yield(t)

    # relations
    w = []
    for t in ('*', 'relation', 'area'):
        if t in where_clauses:
            w.append(where_clauses[t])

    if len(w):
        q = qry.replace('__QRY__', '((' + ');('.join(w) + ');)')
        q = q.replace('__TYPE__', 'relation')
        plpy.warning(q)

        url = 'http://overpass-api.de/api/interpreter?' +\
            urllib.parse.urlencode({ 'data': q })
        f = urllib.request.urlopen(url).read().decode('utf-8')
        res = json.loads(f)

        for r in res['elements']:
            if r['id'] in rels_done:
                pass
            rels_done.append(r['id'])

            g = relation_geom(r)
            if not g or not 'tags' in r:
                continue
            t = {
                'id': 'r' + str(r['id']),
                'types': ['area', 'relation'],
                'tags': r['tags'] if 'tags' in r else {},
                'geo': g
            }
            t['tags']['osm:id'] = t['id']
            t['tags']['osm:version'] = str(r['version']) if 'version' in r else ''
            t['tags']['osm:user_id'] = str(r['uid']) if 'uid' in r else ''
            t['tags']['osm:user'] = r['user'] if 'user' in r else ''
            t['tags']['osm:timestamp'] = r['timestamp'] if 'timestamp' in r else ''
            t['tags']['osm:changeset'] = str(r['changeset']) if 'changeset' in r else ''
            yield(t)

    # areas
    w = []
    for t in ('*', 'relation', 'area'):
        if t in where_clauses:
            w.append(where_clauses[t])

    if len(w):
        plan = plpy.prepare("select ST_Y(ST_Centroid($1::geometry)) || ',' || ST_X(ST_Centroid($1::geometry)) as geom", [ 'geometry' ])
        res = plpy.execute(plan, [ _bbox ])

        q = qry.replace('__QRY__', 'is_in({0});way(pivot);out meta geom;is_in({0});relation(pivot)'.format(res[0]['geom']))
        plpy.warning(q)

        url = 'http://overpass-api.de/api/interpreter?' +\
            urllib.parse.urlencode({ 'data': q })
        f = urllib.request.urlopen(url).read().decode('utf-8')
        res = json.loads(f)

        for r in res['elements']:
            if (r['type'] == 'way' and r['id'] in ways_done) or\
               (r['type'] == 'relation' and r['id'] in rels_done):
                continue

            t = {
                'tags': r['tags'] if 'tags' in r else {},
            }
            if r['type'] == 'relation':
                t['id'] = 'r' + str(r['id'])
                t['types'] = ['area', 'relation']
                t['geo'] = relation_geom(r)
            elif r['type'] == 'way':
                t['id'] = 'w' + str(r['id'])
                t['types'] = ['area', 'line', 'way']
                t['geo'] = way_geom(r, True)
            t['tags']['osm:id'] = t['id']
            t['tags']['osm:version'] = str(r['version']) if 'version' in r else ''
            t['tags']['osm:user_id'] = str(r['uid']) if 'uid' in r else ''
            t['tags']['osm:user'] = r['user'] if 'user' in r else ''
            t['tags']['osm:timestamp'] = r['timestamp'] if 'timestamp' in r else ''
            t['tags']['osm:changeset'] = str(r['changeset']) if 'changeset' in r else ''
            yield(t)

    time_stop = datetime.datetime.now() # profiling
    plpy.notice('querying db objects took %.2fs' % (time_stop - time_start).total_seconds())

def objects_by_id(id_list):
    _id_list = [ int(i[1:]) for i in id_list if i[0] == 'n' ]
    plan = plpy.prepare('select id, tags, geom from nodes where id=any($1)', ['bigint[]']);
    res = plpy.cursor(plan, [_id_list])
    for r in res:
        yield {
            'id': 'n' + str(r['id']),
            'members': [],
            'tags': pghstore.loads(r['tags']),
            'geo': r['geom'],
            'types': ['node', 'point']
        }

    _id_list = [ int(i[1:]) for i in id_list if i[0] == 'w' ]
    plan = plpy.prepare('select id, tags, version, user_id, (select name from users where id=user_id) as user, tstamp, changeset_id, linestring as linestring, array_agg(node_id) as member_ids from (select ways.*, node_id from ways left join way_nodes on ways.id=way_nodes.way_id where ways.id=any($1) order by way_nodes.sequence_id) t group by id, tags, version, user_id, tstamp, changeset_id, linestring', ['bigint[]']);
    res = plpy.cursor(plan, [_id_list])
    for r in res:
        t = {
            'id': 'w' + str(r['id']),
            'members': [ {
                    'member_id': 'n' + str(m),
                    'sequence_id': str(i)
                }
                for i, m in enumerate(r['member_ids'])
            ],
            'tags': pghstore.loads(r['tags']),
            'geo': r['linestring'],
            'types': ['way', 'line', 'area']
        }
        t['tags']['osm:id'] = str(t['id'])
        t['tags']['osm:version'] = str(r['version'])
        t['tags']['osm:user_id'] = str(r['user_id'])
        t['tags']['osm:user'] = r['user']
        t['tags']['osm:timestamp'] = str(r['tstamp'])
        t['tags']['osm:changeset'] = str(r['changeset_id'])
        yield(t)

    _id_list = [ int(i[1:]) for i in id_list if i[0] == 'r' ]
    plan = plpy.prepare('select id, tags, version, user_id, (select name from users where id=user_id) as user, tstamp, changeset_id, array_agg(lower(member_type) || member_id) as member_ids, array_agg(member_role) as member_roles from (select relations.*, member_type, member_id, member_role from relations left join relation_members on relations.id=relation_members.relation_id where relations.id=any($1) order by relation_members.sequence_id) t group by id, tags, version, user_id, tstamp, changeset_id', ['bigint[]']);
    res = plpy.cursor(plan, [_id_list])
    for r in res:
        t = {
            'id': 'r' + str(r['id']),
            'tags': pghstore.loads(r['tags']),
            'members': [ {
                    'member_id': m[0],
                    'role': m[1],
                    'sequence_id': i
                }
                for i, m in enumerate(zip(r['member_ids'], r['member_roles']))
            ],
            'geo': None,
            'types': ['relation']
        }
        t['tags']['osm:id'] = str(t['id'])
        t['tags']['osm:version'] = str(r['version'])
        t['tags']['osm:user_id'] = str(r['user_id'])
        t['tags']['osm:user'] = r['user']
        t['tags']['osm:timestamp'] = str(r['tstamp'])
        t['tags']['osm:changeset'] = str(r['changeset_id'])
        yield(t)

def objects_member_of(member_id, parent_type, parent_conditions):
    if parent_type == 'relation':
        plan = plpy.prepare('select *, (select name from users where id=user_id) as user from relation_members join relations on relation_members.relation_id=relations.id where member_id=$1 and member_type=$2', ['bigint', 'text']);
        res = plpy.cursor(plan, [int(member_id[1:]), member_id[0:1].upper()])
        for r in res:
            t = {
                'id': 'r' + str(r['id']),
                'tags': pghstore.loads(r['tags']),
                'types': ['relation'],
                'geo': None,
                'link_tags': {
                    'sequence_id': str(r['sequence_id']),
                    'role': str(r['member_role']),
                    'member_id': r['member_type'].lower() + str(r['member_id']),
                }
            }
            t['tags']['osm:id'] = str(t['id'])
            t['tags']['osm:version'] = str(r['version'])
            t['tags']['osm:user_id'] = str(r['user_id'])
            t['tags']['osm:user'] = r['user']
            t['tags']['osm:timestamp'] = str(r['tstamp'])
            t['tags']['osm:changeset'] = str(r['changeset_id'])
            yield(t)

    if parent_type == 'way' and member_id[0] == 'n':
        num_id = int(member_id[1:])
        plan = plpy.prepare('select *, (select name from users where id=user_id) as user from way_nodes join ways on way_nodes.way_id=ways.id where node_id=$1', ['bigint']);
        res = plpy.cursor(plan, [num_id])
        for r in res:
            t = {
                'id': 'w' + str(r['id']),
                'tags': pghstore.loads(r['tags']),
                'types': ['way'],
                'geo': r['linestring'],
                'link_tags': {
                    'member_id': member_id,
                    'sequence_id': str(r['sequence_id'])
                }
            }
            t['tags']['osm:id'] = str(t['id'])
            t['tags']['osm:version'] = str(r['version'])
            t['tags']['osm:user_id'] = str(r['user_id'])
            t['tags']['osm:user'] = r['user']
            t['tags']['osm:timestamp'] = str(r['tstamp'])
            t['tags']['osm:changeset'] = str(r['changeset_id'])
            yield(t)

def objects_members(relation_id, parent_type, parent_conditions):
    ob = list(objects_by_id([relation_id]))

    if not len(ob):
        return

    ob = ob[0]

    link_obs_ids = [ i['member_id'] for i in ob['members'] ]
    link_obs = {}
    for o in objects_by_id(link_obs_ids):
        link_obs[o['id']] = o

    for member in ob['members']:
        if not member['member_id'] in link_obs:
            continue

        ret = link_obs[member['member_id']]

        if parent_type not in ret['types']:
            continue

        ret['link_tags'] = member
        yield ret

def objects_near(max_distance, ob, parent_selector, where_clause, check_geo=None):
    if ob:
        geom = ob['geo']
    elif 'geo' in current['properties'][current['pseudo_element']]:
        geom = current['properties'][current['pseudo_element']]['geo']
    else:
        geom = current['object']['geo']

    if where_clause == '':
        where_clause = 'true'

    max_distance = to_float(eval_metric([ max_distance, 'u' ]))
    if max_distance is None:
        return []
    elif max_distance == 0:
        bbox = geom
    else:
        plan = plpy.prepare('select ST_Transform(ST_Buffer(ST_Transform(ST_Envelope($1), {unit.srs}), $2), {db.srs}) as r', ['geometry', 'float'])
        res = plpy.execute(plan, [ geom, max_distance ])
        bbox = res[0]['r']

    if check_geo == 'within':
        where_clause += " and ST_DWithin(way, $2, 0.0)"
    elif check_geo == 'surrounds':
        where_clause += " and ST_DWithin($2, way, 0.0)"
    elif check_geo == 'overlaps':
        where_clause += " and ST_Overlaps($2, way)"

    obs = []
    for ob in objects(
        bbox,
        { parent_selector: where_clause },
        { # add_columns
            '__distance': 'ST_Distance(ST_Transform($2::geometry, {unit.srs}), ST_Transform(__geo__, {unit.srs}))'
        },
        [ 'geometry' ],
        [ geom ]
    ):
        if ob['id'] != current['object']['id'] and ob['__distance'] <= max_distance:
            ob['link_tags'] = {
                'distance': eval_metric([ str(ob['__distance']) + 'u', 'px' ])
            }
            obs.append(ob)

    obs = sorted(obs, key=lambda ob: ob['__distance'] )
    return obs
