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
  r record;
  r1 record;
  sel pgmapcss_selector;
  sel1 pgmapcss_selector;
  ob pgmapcss_selector_part;
  ob1 pgmapcss_selector_part;
  where_selectors pgmapcss_selector[] := Array[]::pgmapcss_selector[];
  assignments hstore := ''::hstore;
  k text;
begin
  for r in select unnest(stat.selectors) selectors, unnest(stat.properties) properties loop
    if (r.properties).prop_has_value ?| (select array_agg(x) from (select unnest(cast((each(stat.prop_style_element)).value as text[])) x) t) then
      where_selectors := array_append(where_selectors, r.selectors);

    elsif (r.properties).has_combine then
      where_selectors := array_append(where_selectors, r.selectors);

    end if;
  end loop;

  -- map conditions which are based on a (possible) set-statement back to their
  -- original selectors
  for r in select
    generate_series(1, array_upper(stat.selectors, 1)) i,
    unnest(stat.selectors) selectors,
    unnest(stat.properties) properties
  loop
    -- TODO: we could check for key/value, hence key=>*
    for r1 in select * from unnest((r.properties).properties) loop
      if r1.assignment_type = 'T' then
	k := quote_nullable(r1.key) || '=>*';
	assignments := assignments || hstore(k,
	  coalesce(assignments->k, '') || ';' || r.i);
      end if;
    end loop;
  end loop;

  -- get all used scale_denominators
  foreach sel in array stat.selectors loop
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
    h := ''::hstore;

    foreach sel in array where_selectors loop
      ob := sel.object;

      if (coalesce(ob.min_scale, 0) <= f) and
	 ((ob.max_scale is null) or (ob.max_scale > f)) then
	c := '(' || pgmapcss_compile_conditions(ob.conditions, '', true) || ')';

	if h ? ob.type then
	  h := h || hstore(ob.type, h->(ob.type) || ' or ' || c);
	else
	  h := h || hstore(ob.type, c);
	end if;

      end if;

      -- include selectors which are referenced through set-statement
      foreach r in array ob.conditions loop
	if assignments ? (quote_nullable(r.key) || '=>*') then
	  k := assignments->(quote_nullable(r.key) || '=>*');

	  foreach c in array string_to_array(substring(k, 2), ';') loop
	    sel1 := (stat.selectors)[cast(c as int)];
	    ob1 := sel1.object;
	    c := '(' || pgmapcss_compile_conditions(ob1.conditions, '', true) || ')';

	    if h ? ob1.type then
	      h := h || hstore(ob1.type, h->(ob1.type) || ' or ' || c);
	    else
	      h := h || hstore(ob1.type, c);
	    end if;
	  end loop;
	end if;
      end loop;
    end loop;

    ret := ret || E'  if render_context.scale_denominator >= ' || f || E' then\n';
    ret := ret || E'    return ' || quote_nullable(cast(h as text)) || E';\n';
    ret := ret || E'  end if;\n\n';
  end loop;

  ret = ret || E'  return ''''::hstore;\n';

  return ret;
end;
$$ language 'plpgsql' immutable;
