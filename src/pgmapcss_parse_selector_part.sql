drop function if exists pgmapcss_parse_selector_part(text);
create or replace function pgmapcss_parse_selector_part (
  text,
  object_class_selector text default '\*|[a-z_]+'
)
returns setof pgmapcss_selector_part
as $$
#variable_conflict use_variable
declare
  ret pgmapcss_selector_part;
  m text;
  m1 text;
  t text;
  selector text;
  max_scale_denominator float := 3.93216e+08;
  r record;
  c pgmapcss_condition;
begin
  selector:=$1;
  ret.classes=Array[]::text[];
  ret.conditions=Array[]::text[];
  ret.pseudo_classes=Array[]::text[];
  ret.pseudo_element := 'default';
  ret.create_pseudo_element := true;

  -- check for comments
  selector := pgmapcss_parse_comments(selector);

  -- parse object class (way, node, canvas, ...)
  m := substring(selector from '^\s*(' || object_class_selector || ')(\|.*|\[.*|:.*|\..*|\s|\{)');
  if m = '*' then
  elsif m is not null then
    ret.type = m;
  else
    raise notice 'can''t parse object class at "%..."', substring(selector, 0, 40);
  end if;
  selector := substring(selector, length(substring(selector from '^(\s*)(' || object_class_selector || ')')) + length(m) + 1);

  -- parse classes
  while selector ~ '^\.([a-zA-Z0-9_]+)' loop
    m := substring(selector from '^\.([a-zA-Z0-9_]+)');
    ret.classes=array_append(ret.classes, m);

    c := ( 'has_tag', '.' || m, null);
    ret.conditions=array_append(ret.conditions, c);

    selector := substring(selector from '^\.[a-zA-Z0-9_]+(.*)$');
  end loop;

  -- parse zoom level
  m := substring(selector from '^\|z([0-9\-]+)(\[.*|:.*|\s)');
  if m is not null then
    -- zN
    m1 := substring(m from '^([0-9]+)$');
    if m1 is not null then
      ret.max_scale := max_scale_denominator / 2 ^ (cast(m as int) - 1);
      ret.min_scale := max_scale_denominator / 2 ^ cast(m as int);
    end if;

    -- zN-
    m1 := substring(m from '^([0-9]+)\-$');
    if m1 is not null then
      ret.max_scale := max_scale_denominator / 2 ^ (cast(m1 as int) - 1);
    end if;

    -- z-N
    m1 := substring(m from '^\-([0-9]+)$');
    if m1 is not null then
      ret.min_scale := max_scale_denominator / 2 ^ cast(m1 as int);
    end if;

    -- zN-N
    m1 := substring(m from '^(?:[0-9]+)\-([0-9]+)$');
    if m1 is not null then
      ret.min_scale := max_scale_denominator / 2 ^ cast(m1 as int);

      m1 := substring(m from '^([0-9]+)\-(?:[0-9]+)$');
      ret.max_scale := max_scale_denominator / 2 ^ (cast(m1 as int) - 1);
    end if;

    selector := substring(selector from '^\|(?:z[0-9\-]+)(\[.*|:.*|\s)');
  end if;

  -- parse condition selector(s)
  while selector ~ '^\[' loop
    r := pgmapcss_parse_condition(substring(selector, 2));
    selector := substring(r.content, 2);
    ret.conditions=array_append(ret.conditions, r.result);
  end loop;

  -- parse pseudo classes
  while selector ~ '^:([a-zA-Z0-9_]+)' loop
    m := substring(selector from '^:([a-zA-Z0-9_]+)');
    ret.pseudo_classes=array_append(ret.pseudo_classes, m);
    selector := substring(selector from '^:[a-zA-Z0-9_]+(.*)$');
  end loop;

  -- parse pseudo element
  if selector ~ '^::([a-zA-Z0-9_\(\)\*]+)' then
    m := substring(selector from '^::([a-zA-Z0-9_\(\)\*]+)');
    m1 := substring(m from '^\((.*)\)$');

    if m1 is not null then
      ret.pseudo_element := m1;
      ret.create_pseudo_element := false;
    else
      ret.pseudo_element := m;
    end if;

    selector := substring(selector from '^::[a-zA-Z0-9_\(\)\*]+(.*)$');
  end if;

  -- check for comments
  ret.text_length=strpos($1, selector) - 1;

  return next ret;
  return;
end;
$$ language 'plpgsql' immutable;
