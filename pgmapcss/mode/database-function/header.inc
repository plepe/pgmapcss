create or replace function pgmapcss_{style_id}(
  IN bbox                geometry,
  IN scale_denominator   float,
  _all_style_elements   text[] default Array['default']
) returns setof pgmapcss_result as $body$

# Compatibility PostgreSQL 9.1: if plpy does not have a cursor interface, map
# it to plpy.execute
if not 'cursor' in dir(plpy):
    plpy.cursor = plpy.execute
