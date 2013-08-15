drop table if exists eval_operators;
create table eval_operators (
  op		text		not null,
  func		text		not null,
  primary key(op)
);
insert into eval_operators values ('+', 'add');
insert into eval_operators values ('-', 'sub');
insert into eval_operators values ('*', 'mul');
insert into eval_operators values ('/', 'div');
insert into eval_operators values ('>', 'gt');
insert into eval_operators values ('>=', 'ge');
insert into eval_operators values ('<=', 'le');
insert into eval_operators values ('<', 'lt');
insert into eval_operators values (',', 'all');
insert into eval_operators values ('==', 'eq');
insert into eval_operators values ('!=', 'neq');
insert into eval_operators values ('<>', 'neq');

create or replace function eval_(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
begin
  return param[array_upper(param, 1)];
end;
$$ language 'plpgsql' immutable;

create or replace function eval_add(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  ret float := 0;
  i text;
begin
  foreach i in array param loop
    ret := ret + cast(eval_number(Array[i], object, current, render_context) as float);
  end loop;

  return ret;
end;
$$ language 'plpgsql' immutable;

create or replace function eval_sub(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  ret float := null;
  i text;
begin
  foreach i in array param loop
    if ret is null then
      ret := i;
    else
      ret := ret - cast(eval_number(Array[i], object, current, render_context) as float);
    end if;
  end loop;

  return ret;
end;
$$ language 'plpgsql' immutable;

create or replace function eval_mul(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  ret float := 1;
  i text;
begin
  foreach i in array param loop
    ret := ret * cast(eval_number(Array[i], object, current, render_context) as float);
  end loop;

  return ret;
end;
$$ language 'plpgsql' immutable;

create or replace function eval_div(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  ret float := 1;
  i text;
begin
  foreach i in array param loop
    ret := ret / cast(eval_number(Array[i], object, current, render_context) as float);
  end loop;

  return ret;
end;
$$ language 'plpgsql' immutable;

create or replace function eval_gt(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  ret text := '';
  i text;
  p1 float;
  p2 float;
begin
  if array_upper(param, 1) >= 2 then
    p1 := cast(eval_number(Array[param[1]], object, current, render_context) as float);
    p2 := cast(eval_number(Array[param[2]], object, current, render_context) as float);
    if p1 > p2 then
      return 'true';
    else
      return 'false';
    end if;
  end if;

  return '';
end;
$$ language 'plpgsql' immutable;

create or replace function eval_ge(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  ret text := '';
  i text;
  p1 float;
  p2 float;
begin
  if array_upper(param, 1) >= 2 then
    p1 := cast(eval_number(Array[param[1]], object, current, render_context) as float);
    p2 := cast(eval_number(Array[param[2]], object, current, render_context) as float);
    if p1 >= p2 then
      return 'true';
    else
      return 'false';
    end if;
  end if;

  return '';
end;
$$ language 'plpgsql' immutable;

create or replace function eval_le(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  ret text := '';
  i text;
  p1 float;
  p2 float;
begin
  if array_upper(param, 1) >= 2 then
    p1 := cast(eval_number(Array[param[1]], object, current, render_context) as float);
    p2 := cast(eval_number(Array[param[2]], object, current, render_context) as float);
    if p1 <= p2 then
      return 'true';
    else
      return 'false';
    end if;
  end if;

  return '';
end;
$$ language 'plpgsql' immutable;

create or replace function eval_lt(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  ret text := '';
  i text;
  p1 float;
  p2 float;
begin
  if array_upper(param, 1) >= 2 then
    p1 := cast(eval_number(Array[param[1]], object, current, render_context) as float);
    p2 := cast(eval_number(Array[param[2]], object, current, render_context) as float);
    if p1 < p2 then
      return 'true';
    else
      return 'false';
    end if;
  end if;

  return '';
end;
$$ language 'plpgsql' immutable;

create or replace function eval_prop(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  i int;
begin
  if array_upper(param, 1) = 0 then
    return '';
  end if;

  if array_upper(param, 1) >= 2 then
    i := array_search(param[2], current.pseudo_elements);

    if i is null then
      return '';
    end if;

  else
    i := current.pseudo_element_ind;

  end if;

  return current.styles[i]->param[1];
end;
$$ language 'plpgsql' immutable;

create or replace function eval_eq(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  ret float := 0;
  i int;
begin
  for i in 2..array_upper(param, 1) loop
    if param[1] != param[i] then
      return 'false';
    end if;
  end loop;

  return 'true';
end;
$$ language 'plpgsql' immutable;

create or replace function eval_neq(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  ret float := 0;
  i int;
begin
  select max(y) into i from (select count(x) y from (select unnest(param) x) t group by x) t;

  if i > 1 then
    return 'true';
  end if;

  return 'false';
end;
$$ language 'plpgsql' immutable;

create or replace function eval_concat(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  ret text := '';
  i text;
begin
  foreach i in array param loop
    ret := ret || i;
  end loop;

  return ret;
end;
$$ language 'plpgsql' immutable;

create or replace function eval_sqrt(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  ret text := '';
  i text;
  p float;
begin
  if array_upper(param, 1) >= 1 then
    p := cast(eval_number(Array[1], object, current, render_context) as float);
    return cast(sqrt(p) as text);
  end if;

  return '';
end;
$$ language 'plpgsql' immutable;

create or replace function eval_boolean(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  ret text := '';
  i text;
begin
  if array_upper(param, 1) >= 1 then
    if param[1] is null or trim(param[1]) in ('', 'no', 'false') or cast(param[1] as float)=0 then
      return 'false';
    else
      return 'true';
    end if;
  end if;

  return '';
end;
$$ language 'plpgsql' immutable;

create or replace function eval_tag(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  i text;
begin
  foreach i in array param loop
    if current.tags ? i then
      return current.tags->i;
    end if;
  end loop;

  return null;
end;
$$ language 'plpgsql' immutable;

create or replace function eval_all(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
begin
  return param[array_upper(param, 1)];
end;
$$ language 'plpgsql' immutable;

create or replace function eval_any(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  r text;
begin
  foreach r in array param loop
    if r is not null and r != '' then
      return r;
    end if;
  end loop;
end;
$$ language 'plpgsql' immutable;

create or replace function eval_cond(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  ret text := '';
  i text;
  result boolean;
begin
  if array_upper(param, 1) >= 2 then
    result := eval_boolean(Array[param[1]], object, current, render_context);

    if result then
      return param[2];
    end if;

    if array_upper(param, 1) >= 3 then
      return param[3];
    end if;
  end if;

  return '';
end;
$$ language 'plpgsql' immutable;

create or replace function eval_number(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  ret text := '';
  unit text := 'px';
  value float;
begin
  if array_upper(param, 1) >= 1 then
    ret := trim(param[1]);

    if ret = '' then
      return '';
    end if;

    if ret ~ '(px|u|m)$' then
      unit := substring(ret from '(px|u|m)$');
      ret := trim(substring(ret, 1, length(ret) - length(unit)));
    end if;

    if ret !~ '^-?[0-9]+(\.[0-9]+)?' then
      return '';
    end if;

    value := cast(ret as float);

    if unit = 'px' or unit is null then
      -- no conversion necessary
    elsif unit in ('u', 'm') then

      value := value / (0.00028 * render_context.scale_denominator);
    else

      return '';
    end if;
  end if;

  if array_upper(param, 1) >= 2 then
    if param[2] = 'px' then
      -- no conversion necessary

    elsif param[2] = 'u' or param[2] = 'm' then
      value := value * (0.00028 * render_context.scale_denominator);

    else
      return '';

    end if;
  end if;

  return cast(value as text);
end;
$$ language 'plpgsql' immutable;

create or replace function eval_list(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
begin
  return array_to_string(param, ';');
end;
$$ language 'plpgsql' immutable;

create or replace function eval_get(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  list text[];
  t text;
  i int;
begin
  if array_upper(param, 1) < 2 then
    return '';
  end if;

  t := eval_number(Array[param[2]], object, current, render_context);

  if t = '' then
    return '';
  end if;

  i := cast(t as int);

  list := string_to_array(param[1], ';');

  if array_upper(list, 1) < i + 1 or i < 0 then
    return '';
  end if;

  return list[i + 1];
end;
$$ language 'plpgsql' immutable;

create or replace function eval_set(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  list text[];
  t text;
  i int;
begin
  if array_upper(param, 1) < 3 then
    return '';
  end if;

  t := eval_number(Array[param[2]], object, current, render_context);

  if t = '' then
    return '';
  end if;

  i := cast(t as int);

  if i < 0 then
    return '';
  end if;

  list := string_to_array(param[1], ';');

  list[i] := param[3];

  return array_to_string(list, ';', '');
end;
$$ language 'plpgsql' immutable;

create or replace function eval_push(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  list text[];
  t text;
  i int;
begin
  if array_upper(param, 1) < 2 then
    return '';
  end if;

  list := string_to_array(param[1], ';');

  list := array_append(list, param[2]);

  return array_to_string(list, ';');
end;
$$ language 'plpgsql' immutable;

create or replace function eval_split(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  list text[];
begin
  if array_upper(param, 1) < 2 then
    return '';
  end if;

  list := string_to_array(param[1], param[2]);

  return array_to_string(list, ';');
end;
$$ language 'plpgsql' immutable;

create or replace function eval_join(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  list text[];
begin
  if array_upper(param, 1) < 2 then
    return '';
  end if;

  list := string_to_array(param[1], ';');

  return array_to_string(list, param[2]);
end;
$$ language 'plpgsql' immutable;

create or replace function eval_count(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  list text[];
begin
  if array_upper(param, 1) < 1 then
    return '';
  end if;

  if param[1] = '' then
    return '0';
  end if;

  list := string_to_array(param[1], ';');

  return array_upper(list, 1);
end;
$$ language 'plpgsql' immutable;

insert into eval_operators values ('~=', 'contains');
create or replace function eval_contains(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  list text[];
  i int;
begin
  if array_upper(param, 1) < 2 then
    return '';
  end if;

  list := string_to_array(param[1], ';');

  select count(*) into i from (select unnest(list) x) t where x=param[2];

  if i = 0 then
    return 'false';
  else
    return 'true';
  end if;
end;
$$ language 'plpgsql' immutable;

create or replace function eval_search(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  list text[];
  i int;
begin
  if array_upper(param, 1) < 2 then
    return '';
  end if;

  list := string_to_array(param[1], ';');

  select n into i from (select generate_series(1, array_upper(list, 1)) n, unnest(list) x) t where x=param[2];

  if i is null then
    return 'false';
  end if;

  return i - 1;
end;
$$ language 'plpgsql' immutable;

create or replace function eval_buffer(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  t text;
begin
  if array_upper(param, 1) < 2 then
    return '';
  end if;

  t := eval_number(Array[param[2], 'u'], object, current, render_context);

  if t is null then
    return '';
  end if;

  return ST_Buffer(param[1], cast(t as float));
end;
$$ language 'plpgsql' immutable;

create or replace function eval_debug(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
begin
  raise notice '%', param[1];

  return param[1];
end;
$$ language 'plpgsql' immutable;

create or replace function eval_TEMPLATE(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
begin
end;
$$ language 'plpgsql' immutable;
