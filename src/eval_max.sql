create or replace function eval_max(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  r text;
  f float;
  max float;
begin
  foreach r in array param loop
    r := eval_number(Array[r], object, current, render_context);

    if r is not null and r != '' then
      f := cast(r as float);

      if max is null or f > max then
	max := f;
      end if;
    end if;
  end loop;

  return coalesce(cast(max as text), '');
end;
$$ language 'plpgsql' immutable;
