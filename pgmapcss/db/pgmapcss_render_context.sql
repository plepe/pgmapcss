create or replace function pgmapcss_render_context (
  bbox geometry,
  scale_denominator float
)
returns pgmapcss_render_context
as $$
#variable_conflict use_variable
declare
  r pgmapcss_render_context;
begin
  r.bbox=bbox;
  r.scale_denominator=scale_denominator;

  return r;
end;
$$ language 'plpgsql' immutable;
