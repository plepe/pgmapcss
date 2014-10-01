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
  style_elements        text[],
  style_elements_index  int[],
  style_elements_layer  float[],
  style_elements_z_index float[]
);

drop table if exists _pgmapcss_left_right_hand_traffic cascade;
create table _pgmapcss_left_right_hand_traffic (
  geo                   geometry
);
create index _pgmapcss_left_right_hand_traffic_geo on _pgmapcss_left_right_hand_traffic using gist(geo);
