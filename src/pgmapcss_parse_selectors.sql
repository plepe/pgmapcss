drop function if exists pgmapcss_parse_selectors(text);
create or replace function pgmapcss_parse_selectors (
  text
)
returns setof pgmapcss_selector
as $$
#variable_conflict use_variable
declare
  r pgmapcss_selector_part;
  rn pgmapcss_selector_part;
  r1 record;
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
	-- if neither >, < or near found, set ''
	tmp.type := '';
	tmp.conditions := Array[]::pgmapcss_condition[];

        ret.link_condition := tmp;
      else
	-- >, <, near
	ret.link_condition := r;
	ret.text_length := ret.text_length + r.text_length;
	content:=substr(content, r.text_length + 1);
      end if;

      r := pgmapcss_parse_selector_part(content);

      -- if link selector is empty, copy conditions on pseudo tags to link condition
      if (ret.link_condition).type = '' then
	tmp := ret.link_condition;
	rn := r;
	rn.conditions := Array[]::pgmapcss_condition[];

	foreach r1 in array r.conditions loop
	  if r1.key in ('role', 'sequence_id') then
	    tmp.conditions := array_append(tmp.conditions, r1);
	  else
	    rn.conditions := array_append(rn.conditions, r1);
	  end if;
	end loop;

	r := rn;
	ret.link_condition := tmp;
      end if;

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
