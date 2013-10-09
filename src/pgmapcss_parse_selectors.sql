drop function if exists pgmapcss_parse_selectors(text);
create or replace function pgmapcss_parse_selectors (
  text
)
returns setof pgmapcss_selector
as $$
#variable_conflict use_variable
declare
  r pgmapcss_selector_part;
  ret pgmapcss_selector;
  content text;
  m text;
  tmp pgmapcss_selector_part;
begin
  content:=$1;

  loop
    r=pgmapcss_parse_selector_part(content);
    content:=substr(content, r.text_length + 1);

    if content !~ '^\s*[,{]' then
      ret.link_parent := r;
      ret.text_length := r.text_length;

      r := pgmapcss_parse_selector_part(content, '>|<|near');
      if r.text_length is null then
	-- if neither >, < or near found, assume '>'
	tmp.type := '>';

        ret.link_condition := tmp;
      else
	-- >, <, near
	ret.link_condition := r;
	ret.text_length := ret.text_length + r.text_length;
	content:=substr(content, r.text_length + 1);
      end if;

      r := pgmapcss_parse_selector_part(content);
      ret.object := r;
      ret.text_length := ret.text_length + r.text_length;
      content:=substr(content, r.text_length + 1);
    else
      ret.object := r;
      ret.text_length := r.text_length;
    end if;

    m := substring(content from '^(\s*,)');
    if m is not null then
      ret.text_length := ret.text_length + length(m);
      content := substring(content, length(m) + 1);

      return next ret;
    else
      return next ret;
      return;
    end if;
  end loop;

  return;
end;
$$ language 'plpgsql' immutable;
