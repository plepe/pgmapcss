drop type if exists pgmapcss_compile_stat cascade;
create type pgmapcss_compile_stat as (
  func          text,
  prop_list     hstore,
  layers	text[]
);
