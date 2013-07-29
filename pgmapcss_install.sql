drop function pgmapcss_install(text, text);
create or replace function pgmapcss_install (
  style_id      text,
  content	text
)
returns text
as $$
#variable_conflict use_variable
declare
  func	text;
begin
  func:=pgmapcss_compile(style_id, content);
  execute func;

  return func;
end;
$$ language 'plpgsql' volatile;
