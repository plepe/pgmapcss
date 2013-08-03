drop type if exists pgmapcss_compile_stat cascade;
create type pgmapcss_compile_stat as (
  func          text,
  prop_list     hstore,
  pseudo_elements	text[]
);

drop type if exists pgmapcss_render_context cascade;
create type pgmapcss_render_context as (
  bbox			geometry,
  scale_denominator	float
);

drop type if exists pgmapcss_object cascade;
create type pgmapcss_object as (
  id			text,
  tags			hstore,
  geo			geometry,
  types			text[]
);

drop type if exists pgmapcss_current cascade;
create type pgmapcss_current as (
  tags			hstore,
  pseudo_element	text,
  pseudo_element_ind	int,
  styles		hstore[],
  has_pseudo_element	boolean[]
);
