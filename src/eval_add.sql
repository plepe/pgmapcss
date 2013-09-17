insert into eval_operators values ('+', 'add');
create or replace function eval_add(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  ret float := 0;
  i text;
  t text;
begin
  foreach i in array param loop
    t := eval_metric(Array[i], object, current, render_context);

    if t = '' then
      return '';
    end if;

    ret := ret + cast(t as float);
  end loop;

  return ret;
end;
$$ language 'plpgsql' immutable;
