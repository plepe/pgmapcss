create or replace function eval_(param text[],
  id text, tags hstore, way geometry, type text[], scale_denominator float, style hstore)
returns text
as $$
#variable_conflict use_variable
declare
begin
  return param[array_upper(param, 1)];
end;
$$ language 'plpgsql' immutable;

create or replace function eval_add(param text[],
  id text, tags hstore, way geometry, type text[], scale_denominator float, style hstore)
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
  id text, tags hstore, way geometry, type text[], scale_denominator float, style hstore)
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
  id text, tags hstore, way geometry, type text[], scale_denominator float, style hstore)
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
  id text, tags hstore, way geometry, type text[], scale_denominator float, style hstore)
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

create or replace function eval_prop(param text[],
  id text, tags hstore, way geometry, type text[], scale_denominator float, style hstore)
returns text
as $$
#variable_conflict use_variable
declare
begin
  foreach i in array param loop
    if style ? i then
      return style->i;
    end if;
  end loop;

  return null;
end;
$$ language 'plpgsql' immutable;

create or replace function eval_tag(param text[],
  id text, tags hstore, way geometry, type text[], scale_denominator float, style hstore)
returns text
as $$
#variable_conflict use_variable
declare
  i text;
begin
  foreach i in array param loop
    if tags ? i then
      return tags->i;
    end if;
  end loop;

  return null;
end;
$$ language 'plpgsql' immutable;

create or replace function eval_all(param text[],
  id text, tags hstore, way geometry, type text[], scale_denominator float, style hstore)
returns text
as $$
#variable_conflict use_variable
declare
begin
  return param[array_upper(param, 1)];
end;
$$ language 'plpgsql' immutable;
