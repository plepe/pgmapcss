insert into eval_operators values ('-', 'sub');
create or replace function eval_sub(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  ret float := null;
  i text;
  t text;
begin
  foreach i in array param loop
    if i = '' or i is null then
      t := '0';
    else
      t := eval_metric(Array[i], object, current, render_context);

      if t = '' then
	return '';
      end if;
    end if;

    if ret is null then
      ret := cast(t as float);
    else
      ret := ret - cast(t as float);
    end if;
  end loop;

  return ret;
end;
$$ language 'plpgsql' immutable;
