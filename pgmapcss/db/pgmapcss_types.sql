-- remove types of pgmapcss version < 0.6
drop type if exists pgmapcss_object cascade;
drop type if exists pgmapcss_parent_object cascade;
drop type if exists pgmapcss_current cascade;

drop type if exists pgmapcss_render_context cascade;
create type pgmapcss_render_context as (
  bbox			geometry,
  scale_denominator	float
);

drop type if exists pgmapcss_result cascade;
create type pgmapcss_result as (
  id			text,
  tags			hstore,
  geo			text,
  types			text[],
  pseudo_element	text,
  properties		hstore,
  "style-element"       text
);
