drop type if exists pgmapcss_compile_stat cascade;
create type pgmapcss_compile_stat as (
  func          text,
  prop_list     hstore,
  layers	text[]
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
  current_layer		text,
  current_layer_ind	int,
  styles		hstore[],
  has_layer		boolean[]
);
