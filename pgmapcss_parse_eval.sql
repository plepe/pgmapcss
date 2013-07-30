-- parse a tree from an eval statement. Returns the tree and the length that was read from the content.
create or replace function pgmapcss_parse_eval(
  			text,
  "offset"		int default 1,
  math_level		int default 0
)
returns pgmapcss_parse_string_return
as $$
#variable_conflict use_variable
declare
  ret pgmapcss_parse_string_return;
  content text;
  esc boolean := false;
  i int;
  j int;
  t text;
  r record;
  a text[];
  current text;
  param text[];
begin
  content := substring($1, "offset");
  ret.text_length := null;

  i := 1;
  current := ''::text;
  param := Array[]::text[];

  loop
    -- raise notice 'eval: % "%..."', math_level, substring(content, i, 20);
    if esc = true then
      current := current || substring(content, i, 1);
      esc := false;

    else
      if substring(content, i, 1) = E'\\' then
	esc := true;

      elsif substring(content, i, 1) in ('"', '''') then
        r := pgmapcss_parse_string(content, null, i + 1);

	current := current || coalesce(r.result, '');
	i := i + r.text_length;

	-- TODO: check no text before / after current

      elsif substring(content, i, 1) = '(' then
	r := pgmapcss_parse_eval(content, i + 1);
        i := i + r.text_length;

	a := cast(r.result as text[]);
	a := array_prepend('f:'||current, a);
	param := array_append(param, cast(a as text));

	current := '';

      elsif substring(content, i, 1) = ')' then
	if current != '' then
	  param := array_append(param, 'v:' || current);
	end if;

	ret.result := cast(param as text);
	ret.text_length := i;
	return ret;
      elsif substring(content, i, 1) = ',' then
	param := array_append(param, 'v:' || current);
	current := '';
      elsif substring(content, i, 1) in ('+', '-', '*', '/') then
        t := substring(content, i, 1);
	j :=  (CASE WHEN t in ('+', '-') THEN 1
	            WHEN t in ('*', '/') THEN 2
	       END);

	if (j < math_level) then
	  if current != '' then
	    param := array_append(param, 'v:' || current);
	  end if;

	  ret.result := cast(param as text);
	  ret.text_length := i - 1;

	  return ret;
	else
	  r := pgmapcss_parse_eval(content, i + 1, j);
	  i := i + r.text_length;

	  a := cast(r.result as text[]);
	  if current = '' then
	    a := array_cat(param, a);
	    a := array_prepend('o:'||t, a);
	    param := a;
	  else
	    a := array_prepend('v:'||current, a);
	    a := array_prepend('o:'||t, a);
	    param := array_append(param, cast(a as text));
	  end if;

	  if substring(content, i, 1) = ')' then
	    i := i - 1;
	  end if;

	end if;

	current := '';
      else
	current := current || substring(content, i, 1);
      end if;
    end if;

    i := i + 1;

    if i > length(content) then
      if current != '' then
	param := array_append(param, 'v:' || current);
      end if;
      ret.result := cast(param as text);
      ret.text_length := i;

      return ret;
    end if;
  end loop;
end;
$$ language 'plpgsql' immutable;
