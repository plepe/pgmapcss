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

drop type if exists pgmapcss_parent_object cascade;
create type pgmapcss_parent_object as (
  id			text,
  tags			hstore,
  geo			geometry,
  types			text[],
  link_tags		hstore
);

drop type if exists pgmapcss_current cascade;
create type pgmapcss_current as (
  tags			hstore,
  parent_object		pgmapcss_parent_object,
  link_object		pgmapcss_object,
  types			text[],
  pseudo_elements	text[],
  pseudo_element_ind	int,
  styles		hstore[],
  has_pseudo_element	boolean[]
);

drop type if exists pgmapcss_result cascade;
create type pgmapcss_result as (
  id			text,
  tags			hstore,
  geo			text,
  types			text[],
  pseudo_element	text,
  properties		hstore,
  "style-element"       text,
  combine_type		text,
  combine_id		text
);
