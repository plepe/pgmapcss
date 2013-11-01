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
    if param[1] is null or trim(param[1]) in ('', 'no', 'false') or param[1] ~ '^[\-\+]?0+(\.0+)?$' then
      return 'false';
    else
      return 'true';
    end if;
  end if;

  return '';
end;
$$ language 'plpgsql' immutable;
