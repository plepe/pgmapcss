create or replace function pgmapcss_compile_selector_part (
  selector pgmapcss_selector_part
)
returns text
as $$
#variable_conflict use_variable
declare
  ret text := '';
begin
  if array_upper(selector.conditions, 1) is null then
    ret = ret || 'true';
  else
    ret = ret || array_to_string((select array_agg(x) from (select pgmapcss_compile_condition(unnest(selector.conditions), 'current.') x) t), ' and ');
  end if;

  if selector.type is not null then
    ret := ret || ' and ''' || selector.type || '''=ANY(object.types)';
  end if;

  if selector.min_scale is not null then
    ret := ret || ' and render_context.scale_denominator >= ' || selector.min_scale;
  end if;
  if selector.max_scale is not null then
    ret := ret || ' and render_context.scale_denominator < ' || selector.max_scale;
  end if;

  return ret;
end;
$$ language 'plpgsql' immutable;
