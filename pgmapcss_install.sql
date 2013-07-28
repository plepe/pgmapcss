create or replace function pgmapcss_install (
  style_id      text,
  content	text
)
returns boolean
as $$
#variable_conflict use_variable
declare
  func	text;
begin
  func:=pgmapcss_compile(style_id, content);
  execute func;

  return true;
end;
$$ language 'plpgsql' volatile;
