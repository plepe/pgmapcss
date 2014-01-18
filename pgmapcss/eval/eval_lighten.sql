create or replace function eval_lighten(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  colors int[];
  factor float;
begin
  if array_upper(param, 1) is null or array_upper(param, 1) < 2 then
    return '';
  end if;

  -- not a valid color
  if not param[1] ~ '^#[0-9a-fA-F]{6,8}' then
    return '';
  end if;

  colors = (select array_agg(s) from (select ('x' || substr(param[1], g * 2 + 2, 2))::bit(8)::int s from generate_series(0, (length(param[1]) - 3) / 2) g) t);
  factor = pgmapcss_to_float(param[2]);

  -- from https://github.com/yvecai/mapnik-opensnowmap.org/blob/master/offset-style/build-relations-style.py
  colors[1] = round((1 - factor) * colors[1] + factor * 255);
  colors[2] = round((1 - factor) * colors[2] + factor * 255);
  colors[3] = round((1 - factor) * colors[3] + factor * 255);

  if array_upper(colors, 1) = 4 then
    return '#' ||
      lpad(to_hex(colors[1]), 2, '0') ||
      lpad(to_hex(colors[2]), 2, '0') ||
      lpad(to_hex(colors[3]), 2, '0') ||
      lpad(to_hex(colors[4]), 2, '0');
  else
    return '#' ||
      lpad(to_hex(colors[1]), 2, '0') ||
      lpad(to_hex(colors[2]), 2, '0') ||
      lpad(to_hex(colors[3]), 2, '0');
  end if;
end;
$$ language 'plpgsql' immutable;


