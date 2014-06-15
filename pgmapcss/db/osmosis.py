# TODO: currently all ways are returned as line and area
# TODO: multipolygons are not supported
# TODO: function objects_member_of(), objects_members(), objects_near() missing
# Use this functions only with a database based on an import with osmosis
def objects(_bbox, where_clauses, add_columns=[], add_param_type=[], add_param_value=[]):
    import pghstore
    time_start = datetime.datetime.now() # profiling

    qry = ''

    if len(add_columns):
        add_columns = ', ' + ', '.join(add_columns)
    else:
        add_columns = ''

    param_type = [ 'geometry' ] + add_param_type
    param_value = [ _bbox ] + add_param_value

    # nodes
    w = []
    for t in ('*', 'node', 'point'):
        if t in where_clauses:
            w.append(where_clauses[t])

    if len(w):
        bbox = ''
        if _bbox is not None:
            bbox = 'geom && ST_Transform($1, 4326) and'

        qry = '''
select 'n' || cast(id as text) as id,
       tags, ST_Transform(geom, 900913) as geo, Array['point', 'node'] as types
       {add_columns}
from nodes
where {bbox} ( {w} )
'''.format(bbox=bbox, w=' or '.join(w), add_columns=add_columns)

        plan = plpy.prepare(qry, param_type )
        res = plpy.execute(plan, param_value )

        for r in res:
            r['tags'] = pghstore.loads(r['tags'])
            yield(r)

    # ways
    w = []
    for t in ('*', 'line', 'area', 'way'):
        if t in where_clauses:
            w.append(where_clauses[t])

    if len(w):
        bbox = ''
        if _bbox is not None:
            bbox = 'linestring && ST_Transform($1, 4326) and'

        qry = '''
select 'w' || cast(id as text) as id,
       tags, ST_Transform(linestring, 900913) as geo, Array['line', 'way', 'area'] as types
       {add_columns}
from ways
where {bbox} ( {w} )
'''.format(bbox=bbox, w=' or '.join(w), add_columns=add_columns)

        plan = plpy.prepare(qry, param_type )
        res = plpy.execute(plan, param_value )

        for r in res:
            r['tags'] = pghstore.loads(r['tags'])
            yield(r)

    # relations - (no bbox match!)
    w = []
    for t in ('*', 'relation'):
        if t in where_clauses:
            w.append(where_clauses[t])

    if len(w):
        qry = '''
select 'r' || cast(id as text) as id,
       tags, null as geo, Array['relation'] as types
       {add_columns}
from relations
where {w}
'''.format(w=' or '.join(w), add_columns=add_columns)

        plan = plpy.prepare(qry, param_type )
        res = plpy.execute(plan, param_value )

        for r in res:
            r['tags'] = pghstore.loads(r['tags'])
            yield(r)

    time_stop = datetime.datetime.now() # profiling
    plpy.notice('querying db objects took %.2fs' % (time_stop - time_start).total_seconds())

def objects_by_id(id_list):
    _id_list = [ int(i[1:]) for i in id_list if i[0] == 'n' ]
    plan = plpy.prepare('select id, tags, ST_Transform(geom, 900913) as geom from nodes where id=any($1)', ['bigint[]']);
    res = plpy.execute(plan, [_id_list])
    for r in res:
        yield {
            'id': 'n' + str(r['id']),
            'members': [],
            'tags': pghstore.loads(r['tags']),
            'geo': r['geom'],
            'types': ['node', 'point']
        }

    _id_list = [ int(i[1:]) for i in id_list if i[0] == 'w' ]
    plan = plpy.prepare('select id, tags, ST_Transform(linestring, 900913) as linestring, array_agg(node_id) as member_ids from (select ways.*, node_id from ways left join way_nodes on ways.id=way_nodes.way_id where ways.id=any($1) order by way_nodes.sequence_id) t group by id, tags, linestring', ['bigint[]']);
    res = plpy.execute(plan, [_id_list])
    for r in res:
        yield {
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

    _id_list = [ int(i[1:]) for i in id_list if i[0] == 'r' ]
    plan = plpy.prepare('select id, tags, array_agg(lower(member_type) || member_id) as member_ids, array_agg(member_role) as member_roles from (select relations.*, member_type, member_id, member_role from relations left join relation_members on relations.id=relation_members.relation_id where relations.id=any($1) order by relation_members.sequence_id) t group by id, tags', ['bigint[]']);
    res = plpy.execute(plan, [_id_list])
    for r in res:
        yield {
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

#def objects_member_of(member_id, parent_type, parent_conditions):
#    if parent_type == 'relation':
#        plan = plpy.prepare('select * from relation_members join relation on relation_members.relation_id=relations.id where member_id @> Array[$1] and member_type = $2', ['bigint', 'text']);
#        res = plpy.execute(plan, [member_id[1:], member_id[0:1].upper()])
#        for r in res:
#            for member in flatarray_to_members(r['members']):
#                if member['member_id'] == member_id:
#                    t = {
#                        'id': 'r' + str(r['id']),
#                        'tags': pghstore.loads(r['tags']),
#                        'type': ['relation'],
#                        'geo': None,
#                        'link_tags': member
#                    }
#                    yield(t)
#
#    if parent_type == 'way':
#        num_id = int(member_id[1:])
#        plan = plpy.prepare('select id, nodes, planet_osm_line.tags, way as geo from planet_osm_ways left join planet_osm_line on planet_osm_ways.id=planet_osm_line.osm_id where nodes::bigint[] @> Array[$1]', ['bigint']);
#        res = plpy.execute(plan, [num_id])
#        for r in res:
#            for i, member in enumerate(r['nodes']):
#                if member == num_id:
#                    t = {
#                        'id': 'w' + str(r['id']),
#                        'tags': pghstore.loads(r['tags']),
#                        'type': ['way'],
#                        'geo': r['geo'],
#                        'link_tags': {
#                            'member_id': member_id,
#                            'sequence_id': str(i)
#                        }
#                    }
#                    yield(t)
#
#def objects_members(relation_id, parent_type, parent_conditions):
#    ob = list(objects_by_id([relation_id]))
#
#    if not len(ob):
#        return
#
#    ob = ob[0]
#
#    link_obs_ids = [ i['member_id'] for i in ob['members'] ]
#    link_obs = {}
#    for o in objects_by_id(link_obs_ids):
#        link_obs[o['id']] = o
#
#    for member in ob['members']:
#        if not member['member_id'] in link_obs:
#            continue
#
#        ret = link_obs[member['member_id']]
#
#        if parent_type not in ret['types']:
#            continue
#
#        ret['link_tags'] = member
#        yield ret
#
#def objects_near(max_distance, ob, parent_selector, where_clause):
#    if ob:
#        geom = ob['geo']
#    else:
#        geom = current['properties'][current['pseudo_element']]['geo']
#
#    max_distance = to_float(eval_metric([ max_distance, 'u' ]))
#    if max_distance is None:
#        return []
#
#    plan = plpy.prepare('select ST_Buffer(ST_Envelope($1), $2) as r', ['geometry', 'float'])
#    res = plpy.execute(plan, [ geom, max_distance ])
#    bbox = res[0]['r']
#
#    obs = []
#    for ob in objects(
#        bbox,
#        { parent_selector: where_clause },
#        [ 'ST_Distance($2, way) as __distance' ],
#        [ 'geometry' ],
#        [ geom ]
#    ):
#        if ob['__distance'] <= max_distance:
#            ob['link_tags'] = {
#                'distance': eval_metric([ str(ob['__distance']) + 'u', 'px' ])
#            }
#            obs.append(ob)
#
#    obs = sorted(obs, key=lambda ob: ob['__distance'] )
#    return obs
