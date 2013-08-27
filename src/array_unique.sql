create or replace function array_unique (
  text[]
)
returns text[]
as $$
  select array_agg(el) from (select unnest($1) el group by el) t;
$$ LANGUAGE sql STABLE;
