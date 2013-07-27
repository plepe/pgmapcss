drop type if exists pgmapcss_selector_return cascade;
create type pgmapcss_selector_return as (
  conditions            text[], /* conditional expressions */
  pseudo_classes        text[], /* :closed, ... */
  layer                 text,
  text_length           int
);

drop function pgmapcss_parse_selector(text);
create or replace function pgmapcss_parse_selector (
  text
)
returns setof pgmapcss_selector_return
as $$
#variable_conflict use_variable
declare
  ret pgmapcss_selector_return;
  m text;
  selector text;
begin
  selector:=$1;
  ret.conditions=Array[]::text[];
  ret.pseudo_classes=Array[]::text[];

  -- parse object class (way, node, canvas, ...)
  m := substring(selector from '^(\*|node|way|relation|area|meta|canvas)(\|.*|\[.*|:.*|\s)');
  if m is not null then
    ret.conditions=array_append(ret.conditions, ''''||m||'''=ANY(type)');
  else
    raise notice 'can''t parse object class at "%..."', substring(selector, 0, 40);
  end if;
  selector := substring(selector from '^(?:\*|node|way|relation|area|meta|canvas)(\|.*|\[.*|:.*|\s)');

  -- parse zoom level
  m := substring(selector from '^\|z([0-9\-]+)(\[.*|:.*|\s)');
  if m is not null then
    ret.conditions=array_append(ret.conditions, 'zoom = '||m);
    selector := substring(selector from '^\|(?:z[0-9\-]+)(\[.*|:.*|\s)');
  end if;

  -- parse condition selector(s)
  while selector ~ '^\[[^\]]+\]' loop
    m := substring(selector from '^\[([^\]]+)\]');
    ret.conditions=array_append(ret.conditions, pgmapcss_condition(m));
    selector := substring(selector from '^\[[^\]]+\](.*)$');
  end loop;

  -- parse pseudo classes
  while selector ~ '^:([a-zA-Z0-9_]+)' loop
    m := substring(selector from '^:([a-zA-Z0-9_]+)');
    ret.pseudo_classes=array_append(ret.pseudo_classes, m);
    selector := substring(selector from '^:[a-zA-Z0-9_]+(.*)$');
  end loop;

  -- parse layer
  if selector ~ '^::([a-zA-Z0-9_]+)' then
    m := substring(selector from '^::([a-zA-Z0-9_]+)');
    ret.layer=m;
    selector := substring(selector from '^::[a-zA-Z0-9_]+(.*)$');
  end if;

  ret.text_length=strpos($1, selector);

  return next ret;
  return;
end;
$$ language 'plpgsql' immutable;
