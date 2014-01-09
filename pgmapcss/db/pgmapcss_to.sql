create or replace function pgmapcss_to_float(value text, other float default null)
returns float
as $$
#variable_conflict use_variable
declare
begin
  begin
    return cast(value as float);
  exception
    when others then
      return other;
  end ;
end;
$$ language 'plpgsql' immutable;
