drop function pgmapcss_parse_selectors(text);
create or replace function pgmapcss_parse_selectors (
  text
)
returns setof pgmapcss_selector_return
as $$
#variable_conflict use_variable
declare
  ret pgmapcss_selector_return;
  content text;
  m text;
begin
  content:=$1;

  loop
    ret=pgmapcss_parse_selector(content);
    content:=substr(content, ret.text_length);

    if content ~ '^\s*,' then
      m=substring(content from '^(\s*,\s*)');
      ret.text_length=ret.text_length+length(m);
      return next ret;

      content=substring(content from '^\s*,\s*(.*)$');
    else
      return next ret;
      return;
    end if;
  end loop;

  return;
end;
$$ language 'plpgsql' immutable;
