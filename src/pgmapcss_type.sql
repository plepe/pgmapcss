create or replace function pgmapcss_type_tag_value(param text,
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
begin
  return ((current.tags)->(param));
end;
$$ language 'plpgsql' immutable;

