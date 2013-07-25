drop type if exists pgmapcss_return cascade;
create type pgmapcss_return as (
  layer         text,
  style         hstore
);

create or replace function pgmapcss_test(
  id            text,
  tags          hstore,
  way           geometry,
  type          text[],
  scale_denominator float
)
returns setof pgmapcss_return
as $$
#variable_conflict use_variable
declare
  layers        text[]=Array['default']::text[];
  styles        hstore[]=Array['']::hstore[];
  r             record;
begin
  if 'way'=any(type) and tags @> 'highway=>primary' then
    styles[1]=styles[1] || 'fill=>#ff0000';
  end if;

  for r in
    (select * from
      (select unnest(layers) layer, unnest(styles) style) t
    order by coalesce(cast(style->'object-z-index' as float), 0))
  loop
    return next r;
  end loop;

  return;
end;
$$ language 'plpgsql' immutable;

select * from pgmapcss_test('N1234', 'highway=>primary, bridge=>yes, name=>Foobar'::hstore, null, Array['way']::text[], 4500);
