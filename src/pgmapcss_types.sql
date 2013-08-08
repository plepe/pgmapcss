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

drop type if exists pgmapcss_condition cascade;
create type pgmapcss_condition as (
  op			text,
  key			text,
  value			text,
  text_length		int
);

drop type if exists pgmapcss_selector_part cascade;
create type pgmapcss_selector_part as (
  type			text,   /* node */
  classes		text[], /* .foo */
  min_scale		float,
  max_scale		float,
  conditions            pgmapcss_condition[], /* conditional expressions */
  pseudo_classes        text[], /* :closed, ... */
  pseudo_element        text,
  text_length           int
);

drop type if exists pgmapcss_selector cascade;
create type pgmapcss_selector as (
  link_parent		pgmapcss_selector_part,
  link_condition	pgmapcss_selector_part,
  object		pgmapcss_selector_part,
  text_length		int
);

drop type if exists pgmapcss_rule_properties cascade;
create type pgmapcss_rule_properties as (
  properties            hstore,
  eval_properties	hstore,
  prop_types		hstore,
  assignments		hstore,
  eval_assignments	hstore,
  unassignments		text[],
  text_length           int
);
