create or replace function eval_int(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
begin
  if array_upper(param, 1) is null then
    return '';
  end if;

  begin
    return trunc(cast(param[1] as float));
  exception
    when others then
      return '';
  end ;
end;
$$ language 'plpgsql' immutable;
