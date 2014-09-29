# Use this functions only with a database based on an import with osm2pgsql
def objects(_bbox, where_clauses, add_columns=[], add_param_type=[], add_param_value=[]):
    import pghstore

    qry = ''

    bbox = ''
    if _bbox is not None:
        bbox = 'way && $1 and'

    if len(add_columns):
        add_columns = ', ' + ', '.join(add_columns)
    else:
        add_columns = ''

    param_type = [ 'geometry' ] + add_param_type
    param_value = [ _bbox ] + add_param_value

    # planet_osm_point
    w = []
    for t in ('*', 'node', 'point'):
        if t in where_clauses:
            w.append(where_clauses[t])

    if len(w):
        qry = '''
select 'n' || cast(osm_id as text) as id,
       tags, way as geo, Array['point', 'node'] as types
       {add_columns}
from planet_osm_point
where {bbox} ( {w} )
'''.format(bbox=bbox, w=' or '.join(w), add_columns=add_columns)

        plan = plpy.prepare(qry, param_type )
        res = plpy.execute(plan, param_value )

        for r in res:
            r['tags'] = pghstore.loads(r['tags'])
            r['tags']['osm:id'] = str(r['id'])
            yield(r)

    # planet_osm_line - ways
    w = []
    for t in ('*', 'line', 'way'):
        if t in where_clauses:
            w.append(where_clauses[t])

    if len(w):
        qry = '''
select 'w' || cast(osm_id as text) as id,
       tags, way as geo, Array['line', 'way'] as types
       {add_columns}
from planet_osm_line
where osm_id>0 and {bbox} ( {w} )
'''.format(bbox=bbox, w=' or '.join(w), add_columns=add_columns)

        plan = plpy.prepare(qry, param_type )
        res = plpy.execute(plan, param_value )

        for r in res:
            r['tags'] = pghstore.loads(r['tags'])
            r['tags']['osm:id'] = str(r['id'])
            yield(r)

    # planet_osm_line - relations
    w = []
    for t in ('*', 'line', 'relation'):
        if t in where_clauses:
            w.append(where_clauses[t])

    if len(w):
        qry = '''
select 'r' || cast(-osm_id as text) as id,
       tags, way as geo, Array['line', 'relation'] as types
       {add_columns}
from planet_osm_line
where osm_id<0 and {bbox} ( {w} )
'''.format(bbox=bbox, w=' or '.join(w), add_columns=add_columns)

        plan = plpy.prepare(qry, param_type )
        res = plpy.execute(plan, param_value )

        for r in res:
            r['tags'] = pghstore.loads(r['tags'])
            r['tags']['osm:id'] = str(r['id'])
            yield(r)

    # planet_osm_polygon - ways
    w = []
    for t in ('*', 'area', 'way'):
        if t in where_clauses:
            w.append(where_clauses[t])

    if len(w):
        qry = '''
select 'w' || cast(osm_id as text) as id,
       tags, way as geo, Array['area', 'way'] as types
       {add_columns}
from planet_osm_polygon
where osm_id>0 and {bbox} ( {w} )
'''.format(bbox=bbox, w=' or '.join(w), add_columns=add_columns)

        plan = plpy.prepare(qry, param_type )
        res = plpy.execute(plan, param_value )

        for r in res:
            r['tags'] = pghstore.loads(r['tags'])
            r['tags']['osm:id'] = str(r['id'])
            yield(r)

    # planet_osm_polygon - relations
    w = []
    for t in ('*', 'area', 'relation'):
        if t in where_clauses:
            w.append(where_clauses[t])

    if len(w):
        qry = '''
select 'r' || cast(-osm_id as text) as id,
       tags, way as geo, Array['area', 'relation'] as types
       {add_columns}
from planet_osm_polygon
where osm_id<0 and {bbox} ( {w} )
'''.format(bbox=bbox, w=' or '.join(w), add_columns=add_columns)

        plan = plpy.prepare(qry, param_type )
        res = plpy.execute(plan, param_value )

        for r in res:
            r['tags'] = pghstore.loads(r['tags'])
            r['tags']['osm:id'] = str(r['id'])
            yield(r)

def objects_by_id(id_list):
    _id_list = [ int(i[1:]) for i in id_list if i[0] == 'n' ]
    plan = plpy.prepare('select * from planet_osm_point where osm_id=any($1)', ['bigint[]']);
    res = plpy.execute(plan, [_id_list])
    for r in res:
        t = {
            'id': 'n' + str(r['osm_id']),
            'members': [],
            'tags': pghstore.loads(r['tags']),
            'geo': r['way'],
            'types': ['node', 'point']
        }
        t['tags']['osm:id'] = t['id']
        yield t

    _id_list = [ int(i[1:]) for i in id_list if i[0] == 'w' ]
    plan = plpy.prepare("select t.*, planet_osm_ways.nodes from (select osm_id, tags, way, 'line' as _type from planet_osm_line where osm_id=any($1) union select osm_id, tags, way, 'way' as _type from planet_osm_polygon where osm_id=any($1)) t left join planet_osm_ways on t.osm_id=planet_osm_ways.id", ['bigint[]']);
    res = plpy.execute(plan, [_id_list])
    for r in res:
        t = {
            'id': 'w' + str(r['osm_id']),
            'members': [ {
                    'member_id': 'n' + str(m),
                    'sequence_id': str(i)
                }
                for i, m in enumerate(r['nodes'])
            ],
            'tags': pghstore.loads(r['tags']),
            'geo': r['way'],
            'types': ['way', r['_type']]
        }
        t['tags']['osm:id'] = t['id']
        yield t

    _id_list = [ int(i[1:]) for i in id_list if i[0] == 'r' ]
    plan = plpy.prepare("select id, planet_osm_rels.tags, members, planet_osm_polygon.way from planet_osm_rels left join planet_osm_polygon on -planet_osm_rels.id=planet_osm_polygon.osm_id where id=any($1)", ['bigint[]'])
    res = plpy.execute(plan, [_id_list])
    for r in res:
        t = {
            'id': 'r' + str(r['id']),
            'tags': flatarray_to_tags(r['tags']),
            'members': flatarray_to_members(r['members']),
            'geo': r['way'],
            'types': ['relation'] if r['way'] is None else ['relation', 'area']
        }
        t['tags']['osm:id'] = t['id']
        yield t

def flatarray_to_tags(arr):
    ret = {}
    for i in range(0, len(arr), 2):
        ret[arr[i]] = arr[i + 1]
    return ret

def flatarray_to_members(arr):
    import math
    ret = []
    for i in range(0, len(arr), 2):
        ret.append({
            'member_id': arr[i],
            'role': arr[i + 1],
            'sequence_id': str(math.floor(i / 2))
        })

    return ret

def objects_member_of(member_id, parent_type, parent_conditions):
    if parent_type == 'relation':
        plan = plpy.prepare('select * from planet_osm_rels where members @> Array[$1]', ['text']);
        res = plpy.execute(plan, [member_id])
        for r in res:
            for member in flatarray_to_members(r['members']):
                if member['member_id'] == member_id:
                    t = {
                        'id': 'r' + str(r['id']),
                        'tags': flatarray_to_tags(r['tags']) if r['tags'] else {},
                        'type': ['relation'],
                        'geo': None,
                        'link_tags': member
                    }
                    t['tags']['osm:id'] = t['id']
                    yield(t)

    if parent_type == 'way':
        num_id = int(member_id[1:])
        plan = plpy.prepare('select id, nodes, planet_osm_line.tags, way as geo from planet_osm_ways left join planet_osm_line on planet_osm_ways.id=planet_osm_line.osm_id where nodes::bigint[] @> Array[$1]', ['bigint']);
        res = plpy.execute(plan, [num_id])
        for r in res:
            for i, member in enumerate(r['nodes']):
                if member == num_id:
                    t = {
                        'id': 'w' + str(r['id']),
                        'tags': pghstore.loads(r['tags']) if r['tags'] else {},
                        'type': ['way'],
                        'geo': r['geo'],
                        'link_tags': {
                            'member_id': member_id,
                            'sequence_id': str(i)
                        }
                    }
                    t['tags']['osm:id'] = t['id']
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
    else:
        geom = current['properties'][current['pseudo_element']]['geo']

    if where_clause == '':
        where_clause = 'true'

    max_distance = to_float(eval_metric([ max_distance, 'u' ]))
    if max_distance is None:
        return []
    elif max_distance == 0:
        bbox = geom
    else:
        plan = plpy.prepare('select ST_Buffer(ST_Envelope($1), $2) as r', ['geometry', 'float'])
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
        [ 'ST_Distance($2, way) as __distance' ],
        [ 'geometry' ],
        [ geom ]
    ):
        if ob['__distance'] <= max_distance:
            ob['link_tags'] = {
                'distance': eval_metric([ str(ob['__distance']) + 'u', 'px' ])
            }
            obs.append(ob)

    obs = sorted(obs, key=lambda ob: ob['__distance'] )
    return obs
