create or replace function eval_rgb(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  colors int[];
  i int;
  t1 text;
  t2 text;
begin
  if array_upper(param, 1) is null or array_upper(param, 1) < 3 then
    return '';
  end if;

  for i in 1..3 loop
    t1 = substring(param[i] from '^\s*([0-9]+(?:\.[0-9]+)?)%\s*$');
    t2 = substring(param[i] from '^\s*([0-9]+(?:\.[0-9]+))\s*$');

    if t1 is not null then
      colors[i] = round(cast(t1 as float) * 2.55);

    elsif t2 is not null then
      colors[i] = round(cast(t2 as float) * 255);

    elsif param[i] ~ '^\s*([0-9]+)\s*$' then
      colors[i] = cast(param[i] as int);

    else
      colors[i] = 0;

    end if;

    if colors[i] < 0 then
      colors[i] = 0;
    elsif colors[i] > 255 then
      colors[i] = 255;
    end if;

  end loop;

  return '#' ||
    lpad(to_hex(colors[1]), 2, '0') ||
    lpad(to_hex(colors[2]), 2, '0') ||
    lpad(to_hex(colors[3]), 2, '0');
end;
$$ language 'plpgsql' immutable;



