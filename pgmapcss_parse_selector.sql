drop function pgmapcss_parse_selector(text);
create or replace function pgmapcss_parse_selector (
  text
)
returns text
as $$
#variable_conflict use_variable
declare
  ret text:='';
  m text;
  selector text;
begin
  selector:=$1;

  -- parse object class (way, node, canvas, ...)
  m := substring(selector from '^(\*|node|way|relation|area|meta|canvas)(\|.*|\[.*|:.*|)$');
  if m is not null then
    ret=''''||m||'''=ANY(type)';
  else
    raise notice 'can''t parse object class';
    return null;
  end if;
  selector := substring(selector from '^(?:\*|node|way|relation|area|meta|canvas)(\|.*|\[.*|:.*|)$');

  -- parse zoom level
  m := substring(selector from '^\|z([0-9\-]+)(\[.*|:.*|)$');
  if m is not null then
    ret=ret||' AND zoom = '||m;
    selector := substring(selector from '^\|(?:z[0-9\-]+)(\[.*|:.*|)$');
  end if;

  -- parse condition selector(s)
  while selector ~ '^\[[^\]]+\]' loop
    m := substring(selector from '^\[([^\]]+)\]');
    ret=ret||' AND '||pgmapcss_condition(m);
    selector := substring(selector from '^\[[^\]]+\](.*)$');
  end loop;

  raise notice '%', selector;

  return ret;
end;
$$ language 'plpgsql' immutable;

