-- parse a string from the current content. Returns the parsed string and the length that was read from the content. This function is very similar to pgmapcss_parse_string, but - when eval content is not quoted - checks for correct parenthesis.
create or replace function pgmapcss_parse_eval(
  			text,
  "offset"		int default 1
)
returns pgmapcss_parse_string_return
as $$
#variable_conflict use_variable
declare
  ret pgmapcss_parse_string_return;
  content text;
  esc boolean := false;
  parenthesis_level int := 0;
  i int;
  r record;
begin
  content := substring($1, "offset");
  ret.result := '';

  if content ~ '^("|'')' then
    r := pgmapcss_parse_string(content);
    return r;
  end if;

  i := 1;
  loop
    raise notice 'X % (%): %...', i, parenthesis_level, substring(content, i, 40);
    if esc = true then
      ret.result := ret.result || substring(content, i, 1);
      esc := false;

    else
      if substring(content, i, 1) = E'\\' then
	ret.result := ret.result || substring(content, i, 1);
	esc := true;

      elsif substring(content, i, 1) in ('"', '''') then
        r := pgmapcss_parse_string(content, null, i);
	raise notice 'parse string %', r;

	ret.result := ret.result || substring(content, i, r.text_length);
	i := i + r.text_length - 1;

      elsif substring(content, i, 1) = '(' then
	ret.result := ret.result || substring(content, i, 1);
        parenthesis_level := parenthesis_level + 1;

      elsif substring(content, i, 1) = ')' then
	if parenthesis_level = 0 then
	  ret.text_length := i - 1;

	  return ret;
	end if;

        parenthesis_level := parenthesis_level - 1;
	ret.result := ret.result || substring(content, i, 1);
      else
	ret.result := ret.result || substring(content, i, 1);
      end if;
    end if;

    i := i + 1;

    if i > length(content) then
      raise notice 'error parsing eval: %...', substring(content, i, 40);
      ret.text_length := i;

      return ret;
    end if;
  end loop;
end;
$$ language 'plpgsql' immutable;
