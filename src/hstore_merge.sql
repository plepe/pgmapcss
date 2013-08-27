drop aggregate array_accum(anyarray) cascade;
CREATE AGGREGATE array_accum(anyarray) (
SFUNC=array_cat,
STYPE=anyarray,
INITCOND='{}'
);

create or replace function hstore_merge (
  hstore[]
)
returns hstore
as $$
  select hstore(array_agg(k), array_agg(v)) from (select t.key k, array_to_string(array_unique(array_accum(t.v)), ';') v from (select (each(h)).key, string_to_array((each(h)).value, ';') v from (select unnest($1) h) t) t group by key) t;
$$ LANGUAGE sql STABLE;
