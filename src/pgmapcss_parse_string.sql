drop type if exists pgmapcss_parse_string_return cascade;
create type pgmapcss_parse_string_return as (
  result	text,
  content	text
);

-- parse a string from the current content. Returns the parsed string and the length that was read from the content.
-- no_quote_match: valid string definition if string is not quoted
create or replace function pgmapcss_parse_string(
  			text,
  no_quote_match	text default null,
  "offset"		int default 1
)
returns pgmapcss_parse_string_return
as $$
#variable_conflict use_variable
declare
  ret pgmapcss_parse_string_return;
  content text;
  quote text := null;
  esc boolean := false;
  i int;
  t text;
begin
  content := substring($1, "offset");
  ret.result := '';

  if content ~ '^("|'')' then
    quote := substring(content from '^("|'')');

    i := 2;
    loop
      if esc = true then
	-- Escaped character.
	t := substring(content, i, 1);
	esc := false;

	ret.result := ret.result || (case
	  when t = 'n' then E'\n'
	  else t
	end);
      else
	if substring(content, i, 1) = E'\\' then
	  esc := true;
	elsif substring(content, i, 1) = quote then
	  ret.content = substring(content, i + 1);

	  return ret;
	else
	  ret.result := ret.result || substring(content, i, 1);
	end if;
      end if;

      i := i + 1;

      if i > length(content) then
	ret.result = null;
	ret.content = '';

	return ret;
      end if;
    end loop;

  elsif content ~ no_quote_match then
    ret.result := substring(content from no_quote_match);
    ret.content := substring(content, length(ret.result) + 1);

    return ret;
  end if;

  ret.result = null;
  ret.content = '';
  return ret;
end;
$$ language 'plpgsql' immutable;
