-- parse a string from the current content. Returns the parsed string and the length that was read from the content.
-- no_quote_match: valid string definition if string is not quoted
create or replace function pgmapcss_parse_string(
  			text,
  no_quote_match	text default null,
  "offset"		int default 1,
  OUT result		text,
  OUT content		text
)
as $$
#variable_conflict use_variable
declare
  quote text := null;
  esc boolean := false;
  i int;
  t text;
begin
  content := substring($1, "offset");
  result := '';

  if content ~ '^("|'')' then
    quote := substring(content from '^("|'')');

    i := 2;
    loop
      if esc = true then
	-- Escaped character.
	t := substring(content, i, 1);
	esc := false;

	result := result || (case
	  when t = 'n' then E'\n'
	  else t
	end);
      else
	if substring(content, i, 1) = E'\\' then
	  esc := true;
	elsif substring(content, i, 1) = quote then
	  content = substring(content, i + 1);

	  return;
	else
	  result := result || substring(content, i, 1);
	end if;
      end if;

      i := i + 1;

      if i > length(content) then
	result = null;
	content = '';

	return;
      end if;
    end loop;

  elsif content ~ no_quote_match then
    result := substring(content from no_quote_match);
    content := substring(content, length(result) + 1);

    return;
  end if;

  result = null;
  content = '';
  return;
end;
$$ language 'plpgsql' immutable;
