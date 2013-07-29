drop type if exists pgmapcss_parse_string_return cascade;
create type pgmapcss_parse_string_return as (
  result	text,
  text_length	int
);

-- parse a string from the current content. Returns the parsed string and the length that was read from the content.
create or replace function pgmapcss_parse_string(
  			text,
  no_quote_match	text default null -- valid string definition if string is not quoted
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
begin
  content := $1;
  ret.result := '';

  if content ~ '^("|'')' then
    quote := substring(content from '^("|'')');

    i := 2;
    loop
      if esc = true then
	ret.result := ret.result || substring(content, i, 1);
	esc := false;
      else
	if substring(content, i, 1) = E'\\' then
	  esc := true;
	elsif substring(content, i, 1) = quote then
	  ret.text_length = i;

	  return ret;
	else
	  ret.result := ret.result || substring(content, i, 1);
	end if;
      end if;

      i := i + 1;

      if i > length(content) then
	ret.result = null;
	ret.text_length = 0;

	return ret;
      end if;
    end loop;

  elsif content ~ no_quote_match then
    ret.result := substring(content from no_quote_match);
    ret.text_length := length(ret.result);

    return ret;
  end if;

  ret.result = null;
  ret.text_length = 0;
  return ret;
end;
$$ language 'plpgsql' immutable;
