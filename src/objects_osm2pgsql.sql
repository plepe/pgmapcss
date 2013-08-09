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
      select ''N'' || cast(osm_id as text),
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
      select ''W'' || cast(osm_id as text),
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
      select ''R'' || cast(-osm_id as text),
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
      select ''W'' || cast(osm_id as text),
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
      select ''R'' || cast(-osm_id as text),
             tags, way, Array[''area'', ''relation'']
      from planet_osm_polygon
      where osm_id<0 and ' || bbox || ' (' ||
        array_to_string(w, ' or ') || ')';
  end if;

  return;
end;
$$ language 'plpgsql' immutable;


