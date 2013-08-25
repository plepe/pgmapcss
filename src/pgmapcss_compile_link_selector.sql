create or replace function pgmapcss_compile_link_selector (
  selector pgmapcss_selector
)
returns text
as $$
#variable_conflict use_variable
declare
  r record;
  t text;
begin
  if (selector.link_condition).type = '>' then
    return 'select t_parent_object.* from ' ||
      'objects_relation_member_of(object.id) t_parent_object ' ||
      'where ' || pgmapcss_compile_selector_part(selector.link_parent, 't_parent_object.');

  elsif (selector.link_condition).type = 'near' then
    t := '100';

    foreach r in array (selector.link_condition).conditions loop
      if r.op in ('<', '<=') and r.key = 'distance' then
	t := r.value;
      end if;
    end loop;

    return 'select * from ' ||
      'objects_near(' || quote_nullable(t) || ', object, current, render_context, ' ||
      quote_nullable(cast(hstore((selector.link_parent).type, pgmapcss_compile_conditions((selector.link_parent).conditions)) as text)) ||
      ')';
  else
    raise warning 'Unknown link selector "%"', (selector.link_condition).type;
    return 'select null::text id, null::hstore tags, null::geometry geo, null::text[] types, null::hstore link_tags from generate_series(1, 0)';

  end if;
end;
$$ language 'plpgsql' immutable;
