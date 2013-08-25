create or replace function pgmapcss_compile_link_selector (
  selector pgmapcss_selector
)
returns text
as $$
#variable_conflict use_variable
declare
begin
  if (selector.link_condition).type = 'in' then
    return 'select t_parent_object.* from ' ||
      'objects_relation_member_of(object.id) t_parent_object ' ||
      'where ' || pgmapcss_compile_selector_part(selector.link_parent, 't_parent_object.');

  else
    raise warning 'Unknown link selector "%"', (selector.link_condition).type;
    return 'select null::text id, null::hstore tags, null::geometry geo, null::text[] types, null::hstore link_tags from generate_series(1, 0)';

  end if;
end;
$$ language 'plpgsql' immutable;
