create or replace function pgmapcss_{style_id}(
  IN bbox                geometry,
  IN scale_denominator   float,
  _all_style_elements   text[] default Array['default']
) returns setof pgmapcss_result as $body$
