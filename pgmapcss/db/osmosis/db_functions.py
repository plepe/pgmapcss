# Use this functions only with a database based on an import with osmosis
def objects(_bbox, where_clauses, add_columns={}, add_param_type=[], add_param_value=[]):
    import pghstore
    time_start = datetime.datetime.now() # profiling

    qry = ''

    if len(add_columns):
        add_columns_qry = ', ' + ', '.join([
                q + ' as "' + k + '"'
                for k, q in add_columns.items()
            ])
    else:
        add_columns_qry = ''

    if _bbox:
        param_type = [ 'geometry' ] + add_param_type
        param_value = [ _bbox ] + add_param_value
    else:
        param_type = add_param_type
        param_value = add_param_value

    # nodes
    w = []
    for t in ('*', 'node', 'point'):
        if t in where_clauses:
            w.append(where_clauses[t])

    if len(w):
        bbox = ''
        if _bbox is not None:
            bbox = 'geom && $1 and ST_Intersects(geom, $1::geometry) and'

        qry = '''
select 'n' || cast(id as text) as id, version, user_id, (select name from users where id=user_id) as user, tstamp, changeset_id,
       tags, geom as geo, Array['point', 'node'] as types
       {add_columns}
from nodes
where {bbox} ( {w} )
'''.format(bbox=bbox, w=' or '.join(w), add_columns=add_columns_qry.replace('__geo__', 'geom'))

        plan = plpy.prepare(qry, param_type )
        res = plpy.cursor(plan, param_value )

        for r in res:
            r['types'] = list(r['types'])
            r['tags'] = pghstore.loads(r['tags'])
            r['tags']['osm:id'] = str(r['id'])
            r['tags']['osm:version'] = str(r['version'])
            r['tags']['osm:user_id'] = str(r['user_id'])
            r['tags']['osm:user'] = r['user']
            r['tags']['osm:timestamp'] = str(r['tstamp'])
            r['tags']['osm:changeset'] = str(r['changeset_id'])
            yield(r)

    # ways
    w = []
    for t in ('*', 'line', 'area', 'way'):
        if t in where_clauses:
            w.append(where_clauses[t])

    if len(w):
        bbox = ''
        if _bbox is not None:
            bbox = 'linestring && $1 and (ST_NPoints(linestring) = 1 or ST_Intersects(linestring, $1::geometry)) and'

        qry = '''
select * from (
select 'w' || cast(id as text) as id, version, user_id, (select name from users where id=user_id) as user, tstamp, changeset_id,
       tags, (CASE WHEN ST_NPoints(linestring) >= 4 and ST_IsClosed(linestring) THEN ST_MakePolygon(linestring) ELSE linestring END) as geo, (ST_NPoints(linestring) >= 4) and ST_IsClosed(linestring) as is_closed, Array['line', 'way'] as types '''
# START db.multipolygons
        qry += '''
, (select array_agg(has_outer_tags) from relation_members join multipolygons on relation_members.relation_id=multipolygons.id where relation_members.member_id=ways.id and relation_members.member_type='W' and relation_members.member_role in ('outer', 'exclave')) part_of_mp_outer
        '''
# END db.multipolygons
        qry += '''
       {add_columns}
from ways
where {bbox} ( {w} ) offset 0) t
       {add_columns}
'''.format(bbox=bbox, w=' or '.join(w), add_columns=add_columns_qry.replace('__geo__', 'linestring'))

        plan = plpy.prepare(qry, param_type )
        res = plpy.cursor(plan, param_value )

        for r in res:
            r['types'] = list(r['types'])
            r['tags'] = pghstore.loads(r['tags'])
            if r['is_closed']:
# START db.multipolygons
                if not r['part_of_mp_outer'] or True not in r['part_of_mp_outer']:
# END db.multipolygons
                    r['types'].append('area')
            r['tags']['osm:id'] = str(r['id'])
            r['tags']['osm:version'] = str(r['version'])
            r['tags']['osm:user_id'] = str(r['user_id'])
            r['tags']['osm:user'] = r['user']
            r['tags']['osm:timestamp'] = str(r['tstamp'])
            r['tags']['osm:changeset'] = str(r['changeset_id'])
            yield(r)

    done_multipolygons = set()
# START db.multipolygons
    # multipolygons
    w = []
    for t in ('*', 'relation', 'area'):
        if t in where_clauses:
            w.append(where_clauses[t])

    if len(w):
        bbox = ''
        if _bbox is not None:
            bbox = 'geom && $1 and ST_Intersects(geom, $1::geometry) and'

        qry = '''
select * from (
select (CASE WHEN has_outer_tags THEN 'm' ELSE 'r' END) || cast(id as text) as id, id as rid, version, user_id, (select name from users where id=user_id) as user, tstamp, changeset_id, has_outer_tags,
       tags, geom as geo, Array['area'] as types
       {add_columns}
from (select multipolygons.*, relations.version, relations.user_id, relations.tstamp, relations.changeset_id from multipolygons left join relations on multipolygons.id = relations.id) t
where {bbox} ( {w} ) offset 0) t
       {add_columns}
'''.format(bbox=bbox, w=' or '.join(w), add_columns=add_columns_qry.replace('__geo__', 'linestring'))

        plan = plpy.prepare(qry, param_type )
        res = plpy.cursor(plan, param_value )

        for r in res:
            r['types'] = list(r['types'])
            r['tags'] = pghstore.loads(r['tags'])
            r['tags']['osm:id'] = str(r['id'])
            r['tags']['osm:version'] = str(r['version'])
            r['tags']['osm:user_id'] = str(r['user_id'])
            r['tags']['osm:user'] = r['user']
            r['tags']['osm:timestamp'] = str(r['tstamp'])
            r['tags']['osm:changeset'] = str(r['changeset_id'])
            if r['has_outer_tags']:
                r['tags']['osm:has_outer_tags'] = 'yes'
            else:
                done_multipolygons.add(r['rid'])
                r['types'].append('relation')
            yield(r)
# END db.multipolygons

    # relations - (no bbox match!)
    w = []
    for t in ('*', 'relation'):
        if t in where_clauses:
            w.append(where_clauses[t])

    if len(w):
        qry = '''
select 'r' || cast(id as text) as id, version, user_id, (select name from users where id=user_id) as user, tstamp, changeset_id,
       tags, null as geo, Array['relation'] as types
       {add_columns}
from relations
where ({w}) and not id = ANY(Array[{done}]::bigint[])
'''.format(w=' or '.join(w), add_columns=add_columns_qry, done=','.join({ str(d) for d in done_multipolygons}))

        plan = plpy.prepare(qry, param_type )
        res = plpy.cursor(plan, param_value )

        for r in res:
            r['types'] = list(r['types'])
            r['tags'] = pghstore.loads(r['tags'])
            r['tags']['osm:id'] = str(r['id'])
            r['tags']['osm:version'] = str(r['version'])
            r['tags']['osm:user_id'] = str(r['user_id'])
            r['tags']['osm:user'] = r['user']
            r['tags']['osm:timestamp'] = str(r['tstamp'])
            r['tags']['osm:changeset'] = str(r['changeset_id'])
            yield(r)

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

def objects_member_of(member_id, parent_type, parent_conditions, child_conditions):
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

def objects_members(relation_id, parent_type, parent_conditions, child_conditions):
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

def objects_near(max_distance, ob, parent_selector, where_clause, child_conditions, current, check_geo=None):
    if ob:
        geom = ob['geo']
    elif 'geo' in current['properties'][current['pseudo_element']]:
        geom = current['properties'][current['pseudo_element']]['geo']
    else:
        geom = current['object']['geo']

    if where_clause == '':
        where_clause = 'true'

    max_distance = to_float(eval_metric([ max_distance, 'u' ], current))
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
                'distance': eval_metric([ str(ob['__distance']) + 'u', 'px' ], current)
            }
            obs.append(ob)

    obs = sorted(obs, key=lambda ob: ob['__distance'] )
    return obs
