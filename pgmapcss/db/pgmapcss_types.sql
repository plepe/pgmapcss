-- remove types of pgmapcss version < 0.6
drop type if exists pgmapcss_object cascade;
drop type if exists pgmapcss_parent_object cascade;
drop type if exists pgmapcss_current cascade;
drop type if exists pgmapcss_render_context cascade;

drop type if exists pgmapcss_result cascade;
create type pgmapcss_result as (
  id			text,
  tags			hstore,
  geo			geometry,
  types			text[],
  pseudo_element	text,
  properties		hstore,
  "style-element"       text
);

drop table if exists _pgmapcss_left_right_hand_traffic cascade;
create table _pgmapcss_left_right_hand_traffic (
  geo                   geometry
);
