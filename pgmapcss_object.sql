create or replace function pgmapcss_object (
  id		text,
  tags		hstore,
  geo		geometry,
  types		text[]
)
returns pgmapcss_object
as $$
#variable_conflict use_variable
declare
  r pgmapcss_object;
begin
  r.id=id;
  r.tags=tags;
  r.geo=geo;
  r.types=types;

  return r;
end;
$$ language 'plpgsql' immutable;
