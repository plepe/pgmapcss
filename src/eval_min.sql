create or replace function eval_min(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  r text;
  f float;
  min float;
begin
  foreach r in array param loop
    r := eval_number(Array[r], object, current, render_context);

    if r is not null and r != '' then
      f := cast(r as float);

      if min is null or f < min then
	min := f;
      end if;
    end if;
  end loop;

  return coalesce(cast(min as text), '');
end;
$$ language 'plpgsql' immutable;
