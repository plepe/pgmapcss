create or replace function eval_number(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  ret text := '';
  unit text := 'px';
  value float;
  m text;
begin
  if array_upper(param, 1) >= 1 then
    ret := trim(param[1]);

    if ret = '' or ret is null then
      return '';
    end if;

    if ret ~ '(px|u|m)$' then
      unit := substring(ret from '(px|u|m)$');
      ret := trim(substring(ret, 1, length(ret) - length(unit)));
    end if;

    m := substring(ret from '^(-?[0-9]+(\.[0-9]+)?)');
    if m is null then
      return '';
    end if;

    value := cast(m as float);

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
