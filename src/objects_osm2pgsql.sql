-- Use this functions only with a database based on an import with osm2pgsql
create or replace function objects(render_context pgmapcss_render_context)
returns setof pgmapcss_object
as $$
#variable_conflict use_variable
declare
begin
  return query
    select cast(osm_id as text), tags, way, Array['point', 'node']
    from planet_osm_point
    where way && render_context.bbox;

  return query
    select cast(osm_id as text), tags, way,
      Array['line', (CASE WHEN osm_id<0 THEN 'relation' ELSE 'way' END)]
    from planet_osm_line
    where way && render_context.bbox;

  return query
    select cast(osm_id as text), tags, way,
      Array['area', (CASE WHEN osm_id<0 THEN 'relation' ELSE 'way' END)]
    from planet_osm_polygon
    where way && render_context.bbox;

  return;
end;
$$ language 'plpgsql' immutable;


