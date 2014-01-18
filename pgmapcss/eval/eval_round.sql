create or replace function eval_round(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  f numeric;
  i int;
begin
  if array_upper(param, 1) is null then
    return '';
  end if;

  begin
    f := cast(param[1] as numeric);
  exception
    when others then
      return '';
  end ;

  if array_upper(param, 1) > 1 then
    begin
      i := cast(param[2] as int);
    exception
      when others then
        i := 0;
    end ;

    return round(f, i);
  
  else
    return round(f);

  end if;
end;
$$ language 'plpgsql' immutable;
