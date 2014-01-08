create or replace function hstore_array_append_unique(
  input hstore,
  k text,
  v text
)
returns hstore
as $$
#variable_conflict use_variable
declare
  ret hstore;
  vs text[];
begin
  ret := input;

  if input ? k then
    vs := cast(input->k as text[]);
  else
    vs := Array[]::text[];
  end if;

  if array_search(v, vs) is null then
    vs := array_append(vs, v);
    ret := ret || hstore(k, cast(vs as text));
  end if;

  return ret;
end;
$$ language 'plpgsql' immutable;
