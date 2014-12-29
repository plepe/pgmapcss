# Use this functions only with a database based on an import with osm2pgsql
def objects_bbox(_bbox, db_selects, options, add_columns={}, add_param_type=[], add_param_value=[]):
    import pghstore

    qry = ''

    bbox = ''
    replacements = {
        'parent_bbox': '',
    }

    if _bbox is not None:
        bbox = 'way && $1 and ST_Intersects(way, $1::geometry) and'
        replacements['parent_bbox'] = 'way && $1 and ST_Intersects(way, $1::geometry) and'

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

    # planet_osm_point
    w = []
    for t in ('*', 'node', 'point'):
        if t in db_selects:
            w.append(db_selects[t])

    if len(w):
        qry = '''
select 'n' || cast(osm_id as text) as id,
       way as geo, Array['point', 'node'] as types
# START db.has-hstore
       , tags
# END db.has-hstore
       {sql.columns.node}
       {add_columns}
from planet_osm_point
where {bbox} ( {w} )
'''.format(bbox=bbox, w=' or '.join(w), add_columns=add_columns_qry)

        qry = qry.replace('__PARENT_BBOX__', replacements['parent_bbox'])
        qry = qry.replace('__TYPE_SHORT__', 'n')
        qry = qry.replace('__TYPE_MODIFY__', '')

        plan = plpy.prepare(qry, param_type )
        res = plpy.cursor(plan, param_value )

        for r in res:
            t = {
                'id': r['id'],
                'geo': r['geo'],
                'types': r['types'],
            }

# START db.columns.node
            t['tags'] = {
                k: r[k]
                for k in r
                if k not in ['id', 'geo', 'types', 'tags'] and k not in add_columns
                if r[k] is not None
            }
# START db.has-hstore
            t['tags'] = dict(pghstore.loads(r['tags']).items() | t['tags'].items())
# END db.has-hstore
# END db.columns.node
# START db.hstore-only
            t['tags'] = pghstore.loads(r['tags'])
# END db.hstore-only
            t['tags']['osm:id'] = str(r['id'])

            for k in add_columns:
                t[k] = r[k]

            yield(t)

    # planet_osm_line - ways
    w = []
    for t in ('*', 'line', 'way'):
        if t in db_selects:
            w.append(db_selects[t])

    if len(w):
        qry = '''
select 'w' || cast(osm_id as text) as id,
       way as geo, Array['line', 'way'] as types
# START db.has-hstore
       , tags
# END db.has-hstore
       {sql.columns.way}
       {add_columns}
from planet_osm_line
where osm_id>0 and {bbox} ( {w} )
'''.format(bbox=bbox, w=' or '.join(w), add_columns=add_columns_qry)
        qry = qry.replace('__PARENT_BBOX__', replacements['parent_bbox'])
        qry = qry.replace('__TYPE_SHORT__', 'w')
        qry = qry.replace('__TYPE_MODIFY__', '')

        plan = plpy.prepare(qry, param_type )
        res = plpy.cursor(plan, param_value )

        for r in res:
            t = {
                'id': r['id'],
                'geo': r['geo'],
                'types': r['types'],
            }

# START db.columns.way
            t['tags'] = {
                k: r[k]
                for k in r
                if k not in ['id', 'geo', 'types', 'tags'] and k not in add_columns
                if r[k] is not None
            }
# START db.has-hstore
            t['tags'] = dict(pghstore.loads(r['tags']).items() | t['tags'].items())
# END db.has-hstore
# END db.columns.way
# START db.hstore-only
            t['tags'] = pghstore.loads(r['tags'])
# END db.hstore-only
            t['tags']['osm:id'] = str(r['id'])

            for k in add_columns:
                t[k] = r[k]

            yield(t)

    # planet_osm_line - relations
    w = []
    for t in ('*', 'line', 'relation'):
        if t in db_selects:
            w.append(db_selects[t])

    if len(w):
        qry = '''
select 'r' || cast(-osm_id as text) as id,
       way as geo, Array['line', 'relation'] as types
# START db.has-hstore
       , tags
# END db.has-hstore
       {sql.columns.way}
       {add_columns}
from planet_osm_line
where osm_id<0 and {bbox} ( {w} )
'''.format(bbox=bbox, w=' or '.join(w), add_columns=add_columns_qry)
        qry = qry.replace('__PARENT_BBOX__', replacements['parent_bbox'])
        qry = qry.replace('__TYPE_SHORT__', 'w')
        qry = qry.replace('__TYPE_MODIFY__', '')

        plan = plpy.prepare(qry, param_type )
        res = plpy.cursor(plan, param_value )

        for r in res:
            t = {
                'id': r['id'],
                'geo': r['geo'],
                'types': r['types'],
            }

# START db.columns.way
            t['tags'] = {
                k: r[k]
                for k in r
                if k not in ['id', 'geo', 'types', 'tags'] and k not in add_columns
                if r[k] is not None
            }
# START db.has-hstore
            t['tags'] = dict(pghstore.loads(r['tags']).items() | t['tags'].items())
# END db.has-hstore
# END db.columns.way
# START db.hstore-only
            t['tags'] = pghstore.loads(r['tags'])
# END db.hstore-only
            t['tags']['osm:id'] = str(r['id'])

            for k in add_columns:
                t[k] = r[k]

            yield(t)

    # planet_osm_polygon - ways
    w = []
    for t in ('*', 'area', 'way'):
        if t in db_selects:
            w.append(db_selects[t])

    if len(w):
        qry = '''
select 'w' || cast(osm_id as text) as id,
       way as geo, Array['area', 'way'] as types
# START db.has-hstore
       , tags
# END db.has-hstore
       {sql.columns.way}
       {add_columns}
from planet_osm_polygon
where osm_id>0 and {bbox} ( {w} )
'''.format(bbox=bbox, w=' or '.join(w), add_columns=add_columns_qry)

        qry = qry.replace('__PARENT_BBOX__', replacements['parent_bbox'])
        qry = qry.replace('__TYPE_SHORT__', 'r')
        qry = qry.replace('__TYPE_MODIFY__', '-')

        plan = plpy.prepare(qry, param_type )
        res = plpy.cursor(plan, param_value )

        for r in res:
            t = {
                'id': r['id'],
                'geo': r['geo'],
                'types': r['types'],
            }

# START db.columns.way
            t['tags'] = {
                k: r[k]
                for k in r
                if k not in ['id', 'geo', 'types', 'tags'] and k not in add_columns
                if r[k] is not None
            }
# START db.has-hstore
            t['tags'] = dict(pghstore.loads(r['tags']).items() | t['tags'].items())
# END db.has-hstore
# END db.columns.way
# START db.hstore-only
            t['tags'] = pghstore.loads(r['tags'])
# END db.hstore-only
            t['tags']['osm:id'] = str(r['id'])

            for k in add_columns:
                t[k] = r[k]

            yield(t)

# planet_osm_polygon - relations
    w = []
    for t in ('*', 'area', 'relation'):
        if t in db_selects:
            w.append(db_selects[t])

    if len(w):
        qry = '''
select 'r' || cast(-osm_id as text) as id,
       way as geo, Array['area', 'relation'] as types
# START db.has-hstore
       , tags
# END db.has-hstore
       {sql.columns.way}
       {add_columns}
from planet_osm_polygon
where osm_id<0 and {bbox} ( {w} )
'''.format(bbox=bbox, w=' or '.join(w), add_columns=add_columns_qry)

        qry = qry.replace('__PARENT_BBOX__', replacements['parent_bbox'])
        qry = qry.replace('__TYPE_SHORT__', 'r')
        qry = qry.replace('__TYPE_MODIFY__', '-')

        plan = plpy.prepare(qry, param_type )
        res = plpy.cursor(plan, param_value )

        for r in res:
            t = {
                'id': r['id'],
                'geo': r['geo'],
                'types': r['types'],
            }

# START db.columns.way
            t['tags'] = {
                k: r[k]
                for k in r
                if k not in ['id', 'geo', 'types', 'tags'] and k not in add_columns
                if r[k] is not None
            }
# START db.has-hstore
            t['tags'] = dict(pghstore.loads(r['tags']).items() | t['tags'].items())
# END db.has-hstore
# END db.columns.way
# START db.hstore-only
            t['tags'] = pghstore.loads(r['tags'])
# END db.hstore-only
            t['tags']['osm:id'] = str(r['id'])

            for k in add_columns:
                t[k] = r[k]

            yield(t)

def objects_by_id(id_list, options):
    _id_list = [ int(i[1:]) for i in id_list if i[0] == 'n' ]
    plan = plpy.prepare('select * from planet_osm_point where osm_id=any($1)', ['bigint[]']);
    res = plpy.cursor(plan, [_id_list])
    for r in res:
        t = {
            'id': 'n' + str(r['osm_id']),
            'members': [],
            'geo': r['way'],
            'types': ['node', 'point']
        }
# START db.columns.node
        t['tags'] = {
            k: r[k]
            for k in r
            if k not in ['id', 'geo', 'types', 'tags', 'way', 'osm_id']
            if r[k] is not None
        }
# START db.has-hstore
        t['tags'] = dict(pghstore.loads(r['tags']).items() | t['tags'].items())
# END db.has-hstore
# END db.columns.node
# START db.hstore-only
        t['tags'] = pghstore.loads(r['tags'])
# END db.hstore-only
        t['tags']['osm:id'] = t['id']
        yield t

    _id_list = [ int(i[1:]) for i in id_list if i[0] == 'w' ]
    plan = plpy.prepare("select t.*, planet_osm_ways.nodes from (select osm_id, tags, way, 'line' as _type from planet_osm_line where osm_id=any($1) union select osm_id, tags, way, 'way' as _type from planet_osm_polygon where osm_id=any($1)) t left join planet_osm_ways on t.osm_id=planet_osm_ways.id", ['bigint[]']);
    res = plpy.cursor(plan, [_id_list])
    for r in res:
        t = {
            'id': 'w' + str(r['osm_id']),
            'members': [ {
                    'member_id': 'n' + str(m),
                    'sequence_id': str(i)
                }
                for i, m in enumerate(r['nodes'])
            ],
            'geo': r['way'],
            'types': ['way', r['_type']]
        }
# START db.columns.way
        t['tags'] = {
            k: r[k]
            for k in r
            if k not in ['osm_id', 'geo', 'types', 'tags', 'nodes', '_type', 'way']
            if r[k] is not None
        }
# START db.has-hstore
        t['tags'] = dict(pghstore.loads(r['tags']).items() | t['tags'].items())
# END db.has-hstore
# END db.columns.way
# START db.hstore-only
        t['tags'] = pghstore.loads(r['tags'])
# END db.hstore-only
        t['tags']['osm:id'] = t['id']
        yield t

    _id_list = [ int(i[1:]) for i in id_list if i[0] == 'r' ]
    plan = plpy.prepare("select id, planet_osm_rels.tags, members, planet_osm_polygon.way from planet_osm_rels left join planet_osm_polygon on -planet_osm_rels.id=planet_osm_polygon.osm_id where id=any($1)", ['bigint[]'])
    res = plpy.cursor(plan, [_id_list])
    for r in res:
        t = {
            'id': 'r' + str(r['id']),
            'tags': flatarray_to_tags(r['tags']) if r['tags'] else {},
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

def objects_member_of(objects, other_selects, self_selects, options):
    if 'relation' in other_selects:
        plan = plpy.prepare('select * from planet_osm_rels where members @> Array[$1]', ['text']);
        for o in objects:
            member_id = o['id']

            res = plpy.cursor(plan, [member_id])
            for r in res:
                for member in flatarray_to_members(r['members']):
                    if member['member_id'] == member_id:
                        t = {
                            'id': 'r' + str(r['id']),
                            'tags': flatarray_to_tags(r['tags']) if r['tags'] else {},
                            'types': ['relation'],
                            'geo': None,
                        }
                        t['tags']['osm:id'] = t['id']
                        yield (o, t, member)

    if 'way' in other_selects:
        plan = plpy.prepare('select id, nodes, planet_osm_line.tags, way as geo from planet_osm_ways left join planet_osm_line on planet_osm_ways.id=planet_osm_line.osm_id where nodes::bigint[] @> Array[$1]', ['bigint']);
        for o in objects:
            member_id = o['id']
            num_id = int(member_id[1:])

            res = plpy.cursor(plan, [num_id])
            for r in res:
                for i, member in enumerate(r['nodes']):
                    if member == num_id:
                        t = {
                            'id': 'w' + str(r['id']),
                            'types': ['way'],
                            'geo': r['geo'],
                        }

                        link_tags = {
                            'member_id': member_id,
                            'sequence_id': str(i)
                        }
# START db.columns.way
                        t['tags'] = {
                            k: r[k]
                            for k in r
                            if k not in ['id', 'geo', 'types', 'tags', 'nodes']
                            if r[k] is not None
                        }
# START db.has-hstore
                        if r['tags'] is not None:
                            t['tags'] = dict(pghstore.loads(r['tags']).items() | t['tags'].items())
# END db.has-hstore
# END db.columns.way
# START db.hstore-only
                        if r['tags'] is not None:
                            t['tags'] = pghstore.loads(r['tags'])
# END db.hstore-only
                        t['tags']['osm:id'] = t['id']
                        yield(o, t, link_tags)

def objects_members(objects, other_selects, self_selects, options):
    for _ob in objects:
        # relation don't get 'members' from objects_bbox(), therefore reload object
        ob = list(objects_by_id([ _ob['id'] ], {}))

        if not len(ob):
            continue

        ob = ob[0]

        link_obs_ids = [ i['member_id'] for i in ob['members'] ]
        link_obs = {}
        for o in objects_by_id(link_obs_ids, {}):
            link_obs[o['id']] = o

        for member in ob['members']:
            if not member['member_id'] in link_obs:
                continue

            ret = link_obs[member['member_id']]

            if len(other_selects.keys() - ret['types']):
                yield (_ob, ret, member )

def objects_near(objects, other_selects, self_selects, options):
    # TODO: how to check properties of object (e.g. when geometry has been modified)
    for ob in objects:
        geom = ob['geo']

        max_distance = to_float(eval_metric([ options['distance'], 'u' ]))
        if max_distance is None:
            return
        elif max_distance == 0:
            bbox = geom
        else:
            plan = plpy.prepare('select ST_Transform(ST_Buffer(ST_Transform(ST_Envelope($1), {unit.srs}), $2), {db.srs}) as r', ['geometry', 'float'])
            res = plpy.execute(plan, [ geom, max_distance ])
            bbox = res[0]['r']

        if not 'check_geo' in options:
            pass
        elif options['check_geo'] == 'within':
            where_clause += " and ST_DWithin(way, $2, 0.0)"
        elif options['check_geo'] == 'surrounds':
            where_clause += " and ST_DWithin($2, way, 0.0)"
        elif options['check_geo'] == 'overlaps':
            where_clause += " and ST_Overlaps($2, way)"

        obs = []
        for o in objects_bbox(
            bbox,
            other_selects,
            options,
            { # add_columns
                '__distance': 'ST_Distance(ST_Transform($2::geometry, {unit.srs}), ST_Transform(way, {unit.srs}))'
            },
            [ 'geometry' ],
            [ geom ]
        ):
            if o['id'] != ob['id'] and o['__distance'] <= max_distance:
                link_tags = {
                    'distance': eval_metric([ str(o['__distance']) + 'u', 'px' ])
                }
                obs.append((o, link_tags))

        obs = sorted(obs, key=lambda o: o[0]['__distance'] )
        for o in obs:
            yield((ob, o[0], o[1]))
