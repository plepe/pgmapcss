create or replace function pgmapcss_compile_where (
  stat		pgmapcss_compile_stat
)
returns text
as $$
#variable_conflict use_variable
declare
  ret text:=''::text;
  h hstore;
  scale_denominators float[];
  f float;
  c text;
  sel pgmapcss_selector;
  ob pgmapcss_selector_part;
begin
  -- get all used scale_denominators
  foreach sel in array stat.where_selectors loop
    ob := sel.object;

    f := coalesce(ob.min_scale, 0);
    if array_search(f, scale_denominators) is null then
      scale_denominators := array_append(scale_denominators, f);
    end if;

    f := ob.max_scale;
    if f is not null and array_search(f, scale_denominators) is null then
      scale_denominators := array_append(scale_denominators, f);
    end if;
  end loop;

  -- order scale_denominators descending
  scale_denominators := (select array_agg(s) from (select unnest(scale_denominators) s order by s desc) t);

  -- now iterate through used scale_denominators and collect where_selectors
  foreach f in array scale_denominators loop
    raise notice 'scale >%', f;
    h := ''::hstore;

    foreach sel in array stat.where_selectors loop
      ob := sel.object;

      if (coalesce(ob.min_scale, 0) <= f) and
	 ((ob.max_scale is null) or (ob.max_scale > f)) then
	c := '(' || pgmapcss_compile_conditions(ob.conditions) || ')';

	if h ? ob.type then
	  h := h || hstore(ob.type, h->(ob.type) || ' or ' || c);
	else
	  h := h || hstore(ob.type, c);
	end if;

      end if;
    end loop;

    ret := ret || E'  if render_context.scale_denominator >= ' || f || E' then\n';
    ret := ret || E'    return ' || quote_nullable(cast(h as text)) || E';\n';
    ret := ret || E'  end if;\n\n';
  end loop;

  ret = ret || E'  return ''''::hstore;\n';

  return ret;
end;
$$ language 'plpgsql' immutable;
