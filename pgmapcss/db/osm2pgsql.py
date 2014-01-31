# Use this functions only with a database based on an import with osm2pgsql
def objects(where_clauses):
    import pghstore
#    t = clock_timestamp();

    qry = ''

    bbox = ''
    if 'bbox' in render_context and render_context['bbox'] is not None:
        bbox = 'way && $1 and'

    # planet_osm_point
    w = []
    for t in ('*', 'node', 'point'):
        if t in where_clauses:
            w.append(where_clauses[t])

    if len(w):
        qry = '''
select 'n' || cast(osm_id as text) as id,
       tags, way as geo, Array['point', 'node'] as types
from planet_osm_point
where {bbox} ( {w} )
'''.format(bbox=bbox, w=' or '.join(w))

        plan = plpy.prepare(qry, [ 'geometry' ] )
        res = plpy.execute(plan, [ render_context['bbox'] ])

        for r in res:
            r['tags'] = pghstore.loads(r['tags'])
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
from planet_osm_line
where osm_id>0 and {bbox} ( {w} )
'''.format(bbox=bbox, w=' or '.join(w))

        plan = plpy.prepare(qry, [ 'geometry' ] )
        res = plpy.execute(plan, [ render_context['bbox'] ])

        for r in res:
            r['tags'] = pghstore.loads(r['tags'])
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
from planet_osm_line
where osm_id<0 and {bbox} ( {w} )
'''.format(bbox=bbox, w=' or '.join(w))

        plan = plpy.prepare(qry, [ 'geometry' ] )
        res = plpy.execute(plan, [ render_context['bbox'] ])

        for r in res:
            r['tags'] = pghstore.loads(r['tags'])
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
from planet_osm_polygon
where osm_id>0 and {bbox} ( {w} )
'''.format(bbox=bbox, w=' or '.join(w))

        plan = plpy.prepare(qry, [ 'geometry' ] )
        res = plpy.execute(plan, [ render_context['bbox'] ])

        for r in res:
            r['tags'] = pghstore.loads(r['tags'])
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
from planet_osm_polygon
where osm_id<0 and {bbox} ( {w} )
'''.format(bbox=bbox, w=' or '.join(w))

        plan = plpy.prepare(qry, [ 'geometry' ] )
        res = plpy.execute(plan, [ render_context['bbox'] ])

        for r in res:
            r['tags'] = pghstore.loads(r['tags'])
            yield(r)

#  -- Uncomment this line for profiling information
#  -- raise notice 'querying db objects took %', clock_timestamp() - t;

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
            'sequence_id': math.floor(i / 2)
        })

    return ret

def objects_relation_member_of(member_id, parent_conditions):
    plan = plpy.prepare('select * from planet_osm_rels where members @> Array[$1]', ['text']);
    res = plpy.execute(plan, [member_id])
    for r in res:
        for member in flatarray_to_members(r['members']):
            if member['member_id'] == member_id:
                t = {
                    'id': 'r' + str(r['id']),
                    'tags': flatarray_to_tags(r['tags']),
                    'type': ['relation'],
                    'geo': None,
                    'link_tags': member
                }
                yield(t)
#end;
#$$ language 'plpgsql' immutable;
#
#def objects_near(max_distance, geom, where_clause):
#    max_distance = to_float(eval_metric([ max_distance, 'u' ]))
#    if max_distance is None:
#        raise StopIteration
#
#    plan = plpy.prepare('select *, ST_Distance($1, way) as __distance from
#
#
