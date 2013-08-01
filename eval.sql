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
    ret := ret + cast(i as float);
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
      ret := ret - cast(i as float);
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
    ret := ret * cast(i as float);
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
    ret := ret / cast(i as float);
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
begin
  if array_upper(param, 1) >= 2 then
    if cast(param[1] as float) > cast(param[2] as float) then
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
begin
  if array_upper(param, 1) >= 2 then
    if cast(param[1] as float) >= cast(param[2] as float) then
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
begin
  if array_upper(param, 1) >= 2 then
    if cast(param[1] as float) <= cast(param[2] as float) then
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
begin
  if array_upper(param, 1) >= 2 then
    if cast(param[1] as float) < cast(param[2] as float) then
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
  i text;
begin
  foreach i in array param loop
    if current.styles[current.current_layer_ind] ? i then
      return current.styles[current.current_layer_ind]->i;
    end if;
  end loop;

  return null;
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
begin
  if array_upper(param, 1) >= 1 then
    return cast(sqrt(cast(param[1] as float)) as text);
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
    result := eval_boolean(Array[param[1]], id, tags, way, type, scale_denominator, style);

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

    if ret ~ '(px|u)$' then
      unit := substring(ret from '(px|u)$');
      ret := trim(substring(ret, 1, length(ret) - length(unit)));
    end if;

    if ret !~ '^[0-9]+(\.[0-9]+)?' then
      return '';
    end if;

    value := cast(ret as float);

    if unit = 'px' then
      -- no conversion necessary
    elsif unit in ('u', 'm') then
      value := value / (0.00028 * scale_denominator);
    end if;

    return cast(value as text);
  end if;

  return '';
end;
$$ language 'plpgsql' immutable;
