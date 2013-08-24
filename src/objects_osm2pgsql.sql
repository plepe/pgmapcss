-- Create multicolumn way / tags indexes
do $$
begin
if not exists (
  select 1
  from pg_class
  where relname = 'planet_osm_point_way_tags'
  ) then

  raise notice E'\ncreating multicolumn indexes - please be patient ...';
  create index planet_osm_point_way_tags on planet_osm_point using gist(way, tags);
  create index planet_osm_line_way_tags on planet_osm_line using gist(way, tags);
  create index planet_osm_polygon_way_tags on planet_osm_polygon using gist(way, tags);
end if;
end$$;

-- Create index on planet_osm_rels members array
do $$
begin
if not exists (
  select 1
  from pg_class
  where relname = 'planet_osm_rels_members'
  ) then

  raise notice E'\ncreating planet_osm_rels members index - please be patient ...';
  create index planet_osm_rels_members on planet_osm_rels using gin(members);
end if;
end$$;

-- Use this functions only with a database based on an import with osm2pgsql
create or replace function objects(render_context pgmapcss_render_context, where_clauses hstore)
returns setof pgmapcss_object
as $$
#variable_conflict use_variable
declare
  w text[];
  bbox text;
begin
  if render_context.bbox is null then
    bbox := '';
  else
    bbox := 'way && ' || quote_nullable(cast(render_context.bbox as text)) || ' and';
  end if;

  -- planet_osm_point
  w := Array[]::text[];
  if where_clauses ? '*' then
    w := array_append(w, where_clauses->'*');
  end if;
  if where_clauses ? 'node' then
    w := array_append(w, where_clauses->'node');
  end if;
  if where_clauses ? 'point' then
    w := array_append(w, where_clauses->'point');
  end if;

  if array_upper(w, 1) is not null then
    return query execute '
      select ''n'' || cast(osm_id as text),
             tags, way, Array[''point'', ''node'']
      from planet_osm_point
      where ' || bbox || ' (' ||
        array_to_string(w, ' or ') || ')';
  end if;

  -- planet_osm_line - ways
  w := Array[]::text[];
  if where_clauses ? '*' then
    w := array_append(w, where_clauses->'*');
  end if;
  if where_clauses ? 'line' then
    w := array_append(w, where_clauses->'line');
  end if;
  if where_clauses ? 'way' then
    w := array_append(w, where_clauses->'way');
  end if;

  if array_upper(w, 1) is not null then
    return query execute '
      select ''w'' || cast(osm_id as text),
             tags, way, Array[''line'', ''way'']
      from planet_osm_line
      where osm_id>0 and ' || bbox || ' (' ||
        array_to_string(w, ' or ') || ')';
  end if;

  -- planet_osm_line - relations
  w := Array[]::text[];
  if where_clauses ? '*' then
    w := array_append(w, where_clauses->'*');
  end if;
  if where_clauses ? 'line' then
    w := array_append(w, where_clauses->'line');
  end if;
  if where_clauses ? 'relation' then
    w := array_append(w, where_clauses->'relation');
  end if;

  if array_upper(w, 1) is not null then
    return query execute '
      select ''r'' || cast(-osm_id as text),
             tags, way, Array[''line'', ''relation'']
      from planet_osm_line
      where osm_id<0 and ' || bbox || ' (' ||
        array_to_string(w, ' or ') || ')';
  end if;

  -- planet_osm_polygon - ways
  w := Array[]::text[];
  if where_clauses ? '*' then
    w := array_append(w, where_clauses->'*');
  end if;
  if where_clauses ? 'area' then
    w := array_append(w, where_clauses->'area');
  end if;
  if where_clauses ? 'way' then
    w := array_append(w, where_clauses->'way');
  end if;

  if array_upper(w, 1) is not null then
    return query execute '
      select ''w'' || cast(osm_id as text),
             tags, way, Array[''area'', ''way'']
      from planet_osm_polygon
      where osm_id>0 and ' || bbox || ' (' ||
        array_to_string(w, ' or ') || ')';
  end if;

  -- planet_osm_polygon - relations
  w := Array[]::text[];
  if where_clauses ? '*' then
    w := array_append(w, where_clauses->'*');
  end if;
  if where_clauses ? 'area' then
    w := array_append(w, where_clauses->'area');
  end if;
  if where_clauses ? 'relation' then
    w := array_append(w, where_clauses->'relation');
  end if;

  if array_upper(w, 1) is not null then
    return query execute '
      select ''r'' || cast(-osm_id as text),
             tags, way, Array[''area'', ''relation'']
      from planet_osm_polygon
      where osm_id<0 and ' || bbox || ' (' ||
        array_to_string(w, ' or ') || ')';
  end if;

  return;
end;
$$ language 'plpgsql' immutable;

create or replace function objects_relation(text)
returns setof pgmapcss_parent_object
as $$
#variable_conflict use_variable
declare
  relation_id bigint;
begin
  relation_id := cast(substring($1, 2) as bigint);

  return query select
    'r' || id,
    t.tags,
    ST_Collect(coalesce(planet_osm_line.way, planet_osm_polygon.way)),
    Array['relation'],
    hstore(Array[
      'index', cast("index" as text),
      'member_id', t.member_id,
      'role', member_role
    ])
  from
    (select
      id,
      t.tags,
      "index",
      (array_agg(members))[1] member_id,
      (array_agg(members))[2] member_role
    from
      (select
	id,
	hstore(tags) tags,
	(generate_series(0, array_upper(members, 1) - 1)) / 2 "index",
	unnest(members) members
      from
	planet_osm_rels
      where
	id = relation_id
      ) t
    group by
      id,
      tags,
      "index"
    order by
      "index"
    ) t
  left join
      planet_osm_line
    on
      (-id) = planet_osm_line.osm_id
  left join
      planet_osm_polygon
    on
      (-id) = planet_osm_polygon.osm_id
  where
    t.member_id=member_id
  group by
    t.id, t."index", t.tags, t.member_id, t.member_role
  ;
end;
$$ language 'plpgsql' immutable;

-- returns all relations the supplied feature is member of, with the
-- additional column link_tags, e.g. "role"=>"stop", "index"=>"492", "member_id"=>"n1231934421"
create or replace function objects_relation_member_of(member_id text)
returns setof pgmapcss_parent_object
as $$
#variable_conflict use_variable
declare
  w text[];
  bbox text;
begin
  return query select
    (ob).*
  from
    (select
      objects_relation('r' || id) ob
    from
      planet_osm_rels
    where
      members @> Array[member_id]
    offset 0
    ) t
  where
    (ob).link_tags->'member_id' = member_id
  ;
end;
$$ language 'plpgsql' immutable;
