#[out:json][bbox:{{bbox}}];(way[name=Marschnergasse];way[name=Erdbrustgasse]);out geom meta;
global query_cache
query_cache = []

def overpass_send_query(query, closure_collect, closure_process=None, cl_param=None):
    global query_cache

    query_cache.append(( query, closure_collect, closure_process, cl_param ))

def overpass_run(intro):
    global query_cache
    closure_process = None

    # use "node;out 1 ids;" as separator statement between requests
    total_query = intro + '\nnode;out 1 ids\n'.join([
        query
        for query, closure_collect, closure_process, cl_param in query_cache
    ])

    index = 0
    collect = []

    query, closure_collect, closure_process, cl_param = query_cache[index]
    for r in overpass_query(total_query):
        if r['type'] == 'node' and not 'lat' in r:
            if closure_process:
                for t in closure_process(collect, cl_param):
                    yield t

                collect = []

            index += 1
            query, closure_collect, closure_process, cl_param = query_cache[index]
        else:
            t = closure_collect(r, cl_param)
            if closure_process:
                collect.append(t)
            else:
                yield t

    query_cache = []

def overpass_query(query):
    import urllib.request
    import urllib.parse
    import json

# START db.overpass-profiler
    time_start = datetime.datetime.now()
    time_duration = datetime.timedelta(0)
    download_size = 0
    count = 0
    count_blocks = 0
# END db.overpass-profiler
    url = '{db.overpass-url}/interpreter'
    data = urllib.parse.urlencode({ 'data': query })
    data = data.encode('utf-8')

    try:
        f = urllib.request.urlopen(url, data)
    except urllib.error.HTTPError as err:
        plpy.warning('Overpass query failed:\n' + query)
        raise

    first = True
    done = False
    to_parse = None
    result = None
    block_remains = ''

    while not done:
# START db.overpass-profiler
        count_blocks += 1
# END db.overpass-profiler
        try:
            r = f.read({db.overpass-blocksize})
# START db.overpass-profiler
            download_size += len(r)
# END db.overpass-profiler

            # make sure that result is valid UTF-8
            # thanks to http://rosettacode.org/wiki/Read_a_file_character_by_character/UTF8#Python
            while True:
                try:
                    r = r.decode('utf-8')
                except UnicodeDecodeError:
                    r += f.read(1)
# START db.overpass-profiler
                    download_size += 1
# END db.overpass-profiler
                else:
                    break
        except urllib.error.HTTPError as err:
            plpy.warning('Overpass query failed (after {} features):\n'.format(count) + query)
            raise

        # EOF detected
        if not r:
            done = True

        # areas not initialized -> ignore
        if first and re.search('osm3s_v[0-9\.]+_areas', r):
            f.close()
            return

        if first:
            # maybe we could read whole result in blocksize
            first = False
            try:
                result = json.loads(r)
            except ValueError:
                pass
            else:
                done = True

        # try to read complete elements from block, remember surroundings for
        # later (block_remains)
        if done:
            to_parse = block_remains
        else:
            block_remains += r
            end_last = block_remains.rfind('\n},')
            if end_last != -1:
                start = block_remains.find('"elements": [')
                to_parse = block_remains[0 : end_last] + '}]\n}'
                block_remains = block_remains[0 : start + 13] + block_remains[end_last + 3 :]

        # try to load JSON - if not complete, try after next reading
        if to_parse:
            try:
                result = json.loads(to_parse)
                to_parse = None
            except ValueError:
                pass

# START db.overpass-profiler
        time_duration += (datetime.datetime.now() - time_start)
# END db.overpass-profiler

        # found a result
        if result:
# START db.overpass-profiler
            count += len(result['elements'])
# END db.overpass-profiler
            for e in result['elements']:
                yield e
            result['elements'] = []

# START db.overpass-profiler
        time_start = datetime.datetime.now()
# END db.overpass-profiler

    if 'remark' in result:
        # ignore timeout if it happens in "print"
        if not re.search("Query timed out in \"print\"", data['remark']):
          raise Exception('Error in Overpass API (after {} features): {}\nFailed query was:\n{}'.format(count, data['remark'], query))

    f.close()

# START db.overpass-profiler
    plpy.warning('%s\nquery took %.2fs for %d features (%.1f MB, %d blocks)' % (query, time_duration.total_seconds(), count, download_size / 1024.0 / 1024, count_blocks))
# END db.overpass-profiler

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

    if len(r['geometry']) < 2:
      return None

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
        geom_plan_linemerge = plpy.prepare('select ST_MakePolygon(geom) geom from (select (ST_Dump((ST_LineMerge(ST_Collect(geom))))).geom as geom from (select ST_GeomFromText(unnest($1), 4326) geom) t offset 0) t where ST_NPoints(geom) > 3 and ST_IsClosed(geom)', [ 'text[]' ])

    t = 'MULTIPOLYGON'

    polygons = []
    lines = []
    inner_polygons = []
    inner_lines = []

    for m in r['members']:
        if not 'geometry' in m:
          continue

        if m['role'] in ('outer', ''):
            if len(m['geometry']) < 2:
                pass
            elif len(m['geometry']) > 3 and m['geometry'][0] == m['geometry'][-1]:
                polygons.append(linestring(m['geometry']))
            else:
                lines.append(linestring(m['geometry']))

        elif m['role'] in ('inner'):
            if len(m['geometry']) < 2:
                pass
            elif len(m['geometry']) > 3 and m['geometry'][0] == m['geometry'][-1]:
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
        if len(r['nodes']) < 2:
            return None
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

    plan = plpy.prepare("select ST_YMin($1) || ',' || ST_XMIN($1) || ',' || ST_YMAX($1) || ',' || ST_XMAX($1) as bbox_string", [ 'geometry' ])
    res = plpy.execute(plan, [ _bbox ])
    return res[0]['bbox_string']

def objects_bbox(_bbox, db_selects, options):
    non_relevant_tags = {'type', 'source', 'source:ref', 'source_ref', 'note', 'comment', 'created_by', 'converted_by', 'fixme', 'FIXME', 'description', 'attribution', 'osm:id', 'osm:version', 'osm:user_id', 'osm:user', 'osm:timestamp', 'osm:changeset'}
    done = {
        'ways': [],
        'rels': [],
        'area_ways': []
    }

    qry = ''
    qry_intro = ''
    replacements = {}

    if _bbox:
        qry_intro += '[bbox:' + get_bbox(_bbox) + ']'
        replacements['__BBOX__'] = '(' + get_bbox(_bbox) + ')'
    else:
        replacements['__BBOX__'] = ''

    qry += ';__QRY__;out meta geom;'

    # nodes
    w = []
    for t in ('*', 'node', 'point'):
        if t in db_selects:
            w.append(db_selects[t])

    if len(w):
        parent_query = ''
        for w1 in w:
            if 'parent_query' in w1:
                parent_query += w1['parent_query']

        q = qry.replace('__QRY__', parent_query + '((' + ');('.join([ w1['query'] for w1 in w ]) + ');)')
        q = q.replace('__TYPE__', 'node')
        for r1, r2 in replacements.items():
            q = q.replace(r1, r2)

        overpass_send_query(q, assemble_object)

        #'http://overpass-turbo.eu/?Q=' + q).read()

    # way areas and multipolygons based on outer tags
    w = []
    for t in ('*', 'area'):
        if t in db_selects:
            w.append(db_selects[t])

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

        def cl_mp_collect(r, cl_param):
            if r['type'] == 'way':
                cl_param[0][r['id']] = r
            elif r['type'] == 'relation':
                cl_param[1][r['id']] = r

        def cl_mp_process(items, cl_param):
            _ways = cl_param[0]
            _rels = cl_param[1]
            done = cl_param[2]

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
                    done['rels'].append(rid)
                    for outer in r['members']:
                        if outer['role'] in ('', 'outer'):
                            done['area_ways'].append(outer['ref'])

                    t = assemble_object(r)
                    if t:
                        if len(mp_tags) == 0:
                            t['id'] = 'm' + str(r['id'])
                            t['types'] = ['multipolygon', 'area']
                            t['tags'] = outer_tags
                            t['tags']['osm:id'] = t['id']
                            t['tags']['osm:has_outer_tags'] = 'yes'

                        yield t

            _ways = None
            _rels = None

        overpass_send_query(q, cl_mp_collect, cl_mp_process, ( _ways, _rels, done ))

    # ways - will be run 3 times, first for areas, then lines and finally for not specified ways
    for types in [
            { 'types': ('area',), 'way_polygon': True },
            { 'types': ('line',), 'way_polygon': False },
            { 'types': ('*', 'way'), 'way_polygon': None },
        ]:
        w = []
        for t in types['types']:
            if t in db_selects:
                w.append(db_selects[t])

        if len(w):
            parent_query = ''
            for w1 in w:
                if 'parent_query' in w1:
                    parent_query += w1['parent_query']

            q = qry.replace('__QRY__', parent_query + '((' + ');('.join([ w1['query'] for w1 in w ]) + ');)')
            q = q.replace('__TYPE__', 'way')
            for r1, r2 in replacements.items():
                q = q.replace(r1, r2)

            def cl_ways(r, done):
                if r['id'] in done['ways']:
                    return

                # check, if way was part of multipolygon (with tags from outer
                # ways) -> may not be area
                way_polygon = types['way_polygon']
                if r['id'] in done['area_ways']:
                    if types['way_polygon'] == True:
                        return
                    else:
                        way_polygon = False

                t = assemble_object(r, way_polygon=way_polygon)
                if t:
                    done['ways'].append(r['id'])
                    return t

            overpass_send_query(q, cl_ways, None, done)

    # relations
    w = []
    parent_query = ''
    for t, type_condition in {'*': '', 'relation': '', 'area': "[type~'^multipolygon|boundary$']"}.items():
        if t in db_selects:
            w.append(db_selects[t]['query'].replace('__TYPE__', 'relation' + type_condition))
            if 'parent_query' in db_selects[t]:
                parent_query += db_selects[t]['parent_query']

    if len(w):
        q = qry.replace('__QRY__', parent_query + '((' + ');('.join(w) + ');)')
        for r1, r2 in replacements.items():
            q = q.replace(r1, r2)

        def cl_rels(r, done):
            if r['id'] in done['rels']:
                return
            done['rels'].append(r['id'])

            return assemble_object(r)

        overpass_send_query(q, cl_rels, None, done)

    # areas
    w = []
    for t in ('*', 'area'):
        if t in db_selects:
            w.append(db_selects[t])

    if len(w):
        plan = plpy.prepare("select ST_Y(ST_Centroid($1)) || ',' || ST_X(ST_Centroid($1)) as geom", [ 'geometry' ])
        res = plpy.execute(plan, [ _bbox ])

        q1 = ');('.join([ w1['query'] for w1 in w ]).replace('__TYPE__', 'relation(pivot.a)')
        q2 = ');('.join([ w1['query'] for w1 in w ]).replace('__TYPE__', 'way(pivot.a)')

        q = (';is_in({})->.a;(' + q1 + q2 + ');out meta geom;').format(res[0]['geom'])
        for r1, r2 in replacements.items():
            q = q.replace(r1, r2)

        def cl_ways_rels(r, done):
            if (r['type'] == 'way' and r['id'] in done['ways']) or\
               (r['type'] == 'relation' and r['id'] in done['rels']):
                return

            return assemble_object(r)

        overpass_send_query(q, cl_ways_rels, None, done)

    for r in overpass_run('[out:json][timeout:{db.overpass-timeout}][maxsize:{db.overpass-memory}]' + qry_intro):
        if r:
            yield r

def objects_by_id(id_list, options):
    if len(id_list) == 0:
        return

    q = ''
    multipolygons = []
    for i in id_list:
        if i[0:1] == 'n':
            q += 'node({});'.format(i[1:])
        elif i[0:1] == 'w':
            q += 'way({});'.format(i[1:])
        elif i[0:1] == 'r':
            q += 'relation({});'.format(i[1:])

    if q == '':
        return
    q = '[out:json][timeout:{db.overpass-timeout}][maxsize:{db.overpass-memory}];(' + q + ');out meta geom qt;'

    for r in overpass_query(q):
        t = assemble_object(r)
        if t:
            yield t

def objects_member_of(objects, other_selects, self_selects, options):
    global member_of_cache
    try:
        member_of_cache
    except:
        member_of_cache = {}

    for ob in objects:
        if ob['id'][0] == 'n':
            ob_type = 'node'
            ob_id = int(ob['id'][1:])
        elif ob['id'][0] == 'w':
            ob_type = 'way'
            ob_id = int(ob['id'][1:])
        elif ob['id'][0] == 'r':
            ob_type = 'relation'
            ob_id = int(ob['id'][1:])

        member_of_cache_id = ob_type + '|' + repr(other_selects) + '|' + repr(self_selects)

        if member_of_cache_id not in member_of_cache:
            member_of_cache[member_of_cache_id] = []
            replacements = { '__BBOX__': '(' + get_bbox() + ')' }
            q = '[out:json][timeout:{db.overpass-timeout}][maxsize:{db.overpass-memory}][bbox:' + get_bbox() + '];'

            for si, ss in self_selects.items():
                if 'parent_query' in ss:
                    q += ss['parent_query']
            for oi, os in other_selects.items():
                if 'parent_query' in os:
                    q += os['parent_query']

            q += '(' + ''.join([
                ss['query'].replace('__TYPE__', ob_type)
                for si, ss in self_selects.items()
            ]) + ')->.a;'

            q += '(' + ''.join([
                ss['query'].replace('__TYPE__', si + '(b' + ob_type[0] + '.a)')
                for si, ss in other_selects.items()
            ]) + ');'

            q += 'out meta qt geom;'

            for r1, r2 in replacements.items():
                q = q.replace(r1, r2)

            for r in overpass_query(q):
                t = assemble_object(r)
                if t:
                    member_of_cache[member_of_cache_id].append(t)

        for t in member_of_cache[member_of_cache_id]:
            for m in t['members']:
                if m['member_id'] == ob['id']:
                    link_tags = {
                            'sequence_id': m['sequence_id'],
                            'member_id': m['member_id'],
                    }
                    if 'role' in m:
                        link_tags['role'] = m['role']

                    yield((ob, t, link_tags))

def objects_members(objects, other_selects, self_selects, options):
    global members_cache
    try:
        members_cache
    except:
        members_cache = {}

    q = '[out:json][timeout:{db.overpass-timeout}][maxsize:{db.overpass-memory}];'

    for ob in objects:
        if ob['id'][0] == 'n':
            ob_type = 'node'
            ob_id = int(ob['id'][1:])
        elif ob['id'][0] == 'w':
            ob_type = 'way'
            ob_id = int(ob['id'][1:])
        elif ob['id'][0] == 'r':
            ob_type = 'relation'
            ob_id = int(ob['id'][1:])

        members_cache_id = ob_type + '|' + repr(other_selects) + '|' + repr(self_selects)

        if members_cache_id not in members_cache:
            members_cache[members_cache_id] = { 'self': {}, 'other': [] }
            replacements = { '__BBOX__': '(' + get_bbox() + ')' }
            q = '[out:json][timeout:{db.overpass-timeout}][maxsize:{db.overpass-memory}][bbox:' + get_bbox() + '];'

            for si, ss in self_selects.items():
                if 'parent_query' in ss:
                    q += ss['parent_query']
            q += '(' + ''.join([
                ss['query'].replace('__TYPE__', ob_type)
                for si, ss in self_selects.items()
            ]) + ');'
            q += 'out meta qt geom;'
            # TODO: out body qt; would be sufficient, but need to adapt assemble_object
            for r1, r2 in replacements.items():
                q = q.replace(r1, r2)

            for r in overpass_query(q):
                t = assemble_object(r)
                if t:
                    t['type'] = r['type']
                    members_cache[members_cache_id]['self'][t['id']] = t

            q = '[out:json][timeout:{db.overpass-timeout}][maxsize:{db.overpass-memory}][bbox:' + get_bbox() + '];'

            for si, ss in self_selects.items():
                if 'parent_query' in ss:
                    q += ss['parent_query']
            for oi, os in other_selects.items():
                if 'parent_query' in os:
                    q += os['parent_query']

            q += '(' + ''.join([
                ss['query'].replace('__TYPE__', ob_type)
                for si, ss in self_selects.items()
            ]) + ')->.a;'

            q += '(' + ''.join([
                ss['query'].replace('__TYPE__', si + '(' + ob_type[0] + '.a)')
                for si, ss in other_selects.items()
            ]) + ');'

            q += 'out meta qt geom;'
        # TODO: .a out body qt; would be sufficient, but need to adapt assemble_object
            for r1, r2 in replacements.items():
                q = q.replace(r1, r2)

            for r in overpass_query(q):
                t = assemble_object(r)
                if t:
                    members_cache[members_cache_id]['other'].append(t)

        if not ob['id'] in members_cache[members_cache_id]['self']:
            continue

        relation = members_cache[members_cache_id]['self'][ob['id']]

        for t in members_cache[members_cache_id]['other']:
            for m in relation['members']:
                if m['member_id'] == t['id']:
                    link_tags = {
                        'sequence_id': m['sequence_id'],
                        'member_id': m['member_id'],
                    }
                    if 'role' in m:
                        link_tags['role'] = m['role']

                    yield((ob, t, link_tags))

def objects_near(objects, other_selects, self_selects, options):
    cache_id = 'objects_near' + '|' + repr(other_selects) + '|' + repr(self_selects) + '|' + repr(options)

    max_distance = to_float(eval_metric([ options['distance'], 'u' ]))
    if max_distance is None:
        return

    try:
        cache = get_PGCache(cache_id)
    except:
        cache = PGCache(cache_id, read_geo=True)

        plan = plpy.prepare('select ST_Transform(ST_Envelope(ST_Buffer(ST_Transform(ST_Envelope($1), {unit.srs}), $2)), {db.srs}) as r', ['geometry', 'float'])
        res = plpy.execute(plan, [ render_context['bbox'], max_distance ])
        bbox = res[0]['r']

        for t in objects_bbox(bbox, other_selects, options):
            cache.add(t)

    if not 'check_geo' in options:
        pass
    elif options['check_geo'] == 'within':
        where_clause += " and ST_DWithin(geo, $1, 0.0)"
    elif options['check_geo'] == 'surrounds':
        where_clause += " and ST_DWithin($1, geo, 0.0)"
    elif options['check_geo'] == 'overlaps':
        where_clause += " and ST_Overlaps($1, geo)"

    for ob in objects:
        geom = ob['geo']

        if max_distance == 0:
            bbox = geom
        else:
            plan = plpy.prepare('select ST_Transform(ST_Buffer(ST_Transform(ST_Envelope($1), {unit.srs}), $2), {db.srs}) as r', ['geometry', 'float'])
            res = plpy.execute(plan, [ geom, max_distance ])
            bbox = res[0]['r']

            plan = cache.prepare('select * from (select *, ST_Distance(ST_Transform($1, {unit.srs}), ST_Transform(geo, {unit.srs})) dist from {table} where geo && $2 offset 0) t order by dist asc', [ 'geometry', 'geometry' ])
            for t in cache.cursor(plan, [ geom, bbox ]):
                o = t['data']

                if o['id'] != ob['id'] and t['dist'] <= max_distance:
                    link_tags = {
                        'distance': eval_metric([ str(t['dist']) + 'u', 'px' ])
                    }

                    yield (ob, o, link_tags)
