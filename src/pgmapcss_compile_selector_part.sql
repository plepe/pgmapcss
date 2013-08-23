create or replace function pgmapcss_compile_selector_part (
  selector pgmapcss_selector_part
)
returns text
as $$
#variable_conflict use_variable
declare
  ret text := '';
begin
  ret = ret || pgmapcss_compile_conditions(selector.conditions, 'current.');

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
