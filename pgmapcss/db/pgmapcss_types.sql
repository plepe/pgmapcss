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

drop table if exists _pgmapcss_PGCache cascade;
create table _pgmapcss_PGCache (
  cache_id      int,
  data          bytea,
  id            text,
  geo           geometry
);
create index _pgmapcss_PGCache_cache_id on _pgmapcss_PGCache(cache_id);
create index _pgmapcss_PGCache_id on _pgmapcss_PGCache(id);
create index _pgmapcss_PGCache_geo on _pgmapcss_PGCache using gist(geo);

drop function if exists __eval_test__();

drop table if exists pgmapcss_translations cascade;
create table pgmapcss_translations (
  lang          text,
  key           text,
  value         text,
  primary key(lang, key)
);
