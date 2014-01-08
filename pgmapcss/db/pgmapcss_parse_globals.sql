drop type if exists pgmapcss_globals_return cascade;
create type pgmapcss_globals_return as (
  defines	hstore,
  constants	hstore,
  text_length           int
);

drop function if exists pgmapcss_parse_globals(text);
create or replace function pgmapcss_parse_globals (
  text
)
returns setof pgmapcss_globals_return
as $$
#variable_conflict use_variable
declare
  ret pgmapcss_globals_return;
  r record;
  content text;
  m text;
  k text;
begin
  content := $1;
  ret.constants := ''::hstore;
  ret.defines := ''::hstore;
  ret.text_length := 0;

  loop
    -- check for comments
    content := pgmapcss_parse_comments(content);

    if content ~ '^\s*@[A-Za-z0-9\-_]+\s*:\s*' then
      k := substring(content from '^\s*@([A-Za-z0-9\-_]+)\s*:\s*');

      ret.text_length := ret.text_length +
        length(substring(content from '^(\s*@[A-Za-z0-9\-_]+\s*:\s*)'));

      r := pgmapcss_parse_string(content, '^([^;]+);', ret.text_length);

      raise notice '% %', k, r;

      ret.constants := ret.constants || hstore(k, trim(r.result));
      ret.text_length := ret.text_length + r.text_length;
      content := substring(content, ret.text_length);
      raise notice 'content "% %"', ret.text_length, substring(content, ret.text_length, 40);
    else
      raise notice 'ret %', ret;
      return next ret;
      return;
    end if;
  end loop;

  return;
end;
$$ language 'plpgsql' immutable;
