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

drop type if exists pgmapcss_condition cascade;
create type pgmapcss_condition as (
  op			text,
  key			text,
  value			text,
  -- 0..string, 1..eval expression
  value_type		smallint,
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
  create_pseudo_element	boolean,
  text_length           int
);

drop type if exists pgmapcss_selector cascade;
create type pgmapcss_selector as (
  link_parent		pgmapcss_selector_part,
  link_condition	pgmapcss_selector_part,
  object		pgmapcss_selector_part,
  text_length		int
);

drop type if exists pgmapcss_property cascade;
create type pgmapcss_property as (
  -- 'P'=property, 'T'=tag, 'U'=unset tag, 'C'=combine
  assignment_type	char,
  key			text,
  value			text,
  eval_value		text,
  value_type		smallint,
  -- 0 .. value
  -- 1 .. eval()
  -- 2 .. quoted string
  -- 3 .. rgb()
  -- 4 .. url()
  unit			text
);

drop type if exists pgmapcss_properties cascade;
create type pgmapcss_properties as (
  properties		pgmapcss_property[],
  prop_has_value	hstore,
  has_combine		boolean,
  content		text
);

drop type if exists pgmapcss_compile_stat cascade;
create type pgmapcss_compile_stat as (
  func          text,
  prop_types    hstore,
  prop_default_other 	hstore, -- @default_other statements
  prop_values	hstore, -- @check_value statements
  selectors	pgmapcss_selector[],
  properties	pgmapcss_properties[],
  properties_values	hstore,
  -- where_selectors: all selectors which make an object show
  pseudo_elements	text[]
);

drop type if exists pgmapcss_result cascade;
create type pgmapcss_result as (
  id			text,
  tags			hstore,
  geo			text,
  types			text[],
  pseudo_element	text,
  properties		hstore,
  combine_type		text,
  combine_id		text
);
