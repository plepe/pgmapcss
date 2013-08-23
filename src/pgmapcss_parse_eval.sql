-- parse a tree from an eval statement. Returns the tree and the length that was read from the content.
create or replace function pgmapcss_parse_eval(
  			text,
  "offset"		int default 1,
  math_level		int default 0,
  current_op		text default null
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
  b text[];
  current text;
  current_length int;
  current_whitespace text;
  param text[];
  mode int := 0;
  -- 0 .. reading whitespace before token
  -- 1 .. reading token
  -- 2 .. token finished, read quoted string
  -- 3 .. token finished (e.g. after brackets)
  op_regexp text;
begin
  content := substring($1, "offset");
  ret.text_length := null;
  -- raise notice 'parse_eval(''%'', %, ''%'')', content, math_level, current_op;
  
  -- compile eval operator regexp
  select '^(' || array_to_string(array_agg(x), '|') || ')' into op_regexp from (select replace(regexp_replace(op, '(\+|\*)', E'\\ \\1', 'g'), ' ', '') x from eval_operators) t;

  i := 1;
  current := ''::text;
  current_length := 0;
  current_whitespace := '';
  param := Array[]::text[];

  loop
    -- raise notice 'eval: (math%) (mode%) "%..."', math_level, mode, substring(content, i, 20);
    if esc = true then
      current := current || current_whitespace || substring(content, i, 1);
      current_whitespace := '';
      current_length := current_length + 1;
      esc := false;

    else
      if substring(content, i, 1) = E'\\' then
	esc := true;

	if mode = 0 then
	  mode = 1;
	elsif mode > 1 then
	  raise warning 'Error parsing eval statement at "%..."', substring(content, i, 20);
	end if;

      elsif substring(content, i, 1) in ('"', '''') then
	if current != '' then
	  raise warning 'Error parsing eval statement at "%..."', substring(content, i, 20);
	end if;

        r := pgmapcss_parse_string(content, null, i);

	current := coalesce(r.result, '');
	current_length := current_length + r.text_length;
	current_whitespace := '';
	i := i + r.text_length - 1;

	mode=2;
      elsif substring(content, i, 1) = '(' then
	r := pgmapcss_parse_eval(content, i + 1);
        i := i + r.text_length;

	a := (cast(r.result as text[]));
	if a[1] ~ '^{' then
	  a := a[1];
	end if;

	if a[1] ~ '^o:,' then
	  a[1] := 'f:' || current;
	else
	  a := Array['f:' || current, cast(a as text)];
	end if;

	param := array_append(param, cast(a as text));

	current := '';
	current_whitespace := '';
	current_length := 0;
	mode := 3;

      elsif substring(content, i, 1) = ')' then
	if current != '' then
	  param := array_append(param, 'v:' || current);
	end if;

	ret.result := cast(param as text);
	ret.text_length := i;
	return ret;
      elsif substring(content, i, 2) ~ op_regexp then
        t := substring(substring(content, i, 2) from op_regexp);
	i := i + length(t) - 1;
	j :=  (CASE WHEN t in ('+', '-') THEN 3
	            WHEN t in ('*', '/') THEN 2
	            WHEN t in ('>', '>=', '<=', '<') THEN 2
	            WHEN t in (',', ';') THEN 99
	       END);

	if t = current_op then
	  if current != '' then
	    param := array_append(param, 'v:' || current);
	  end if;
	  mode := 0;
	elsif (j < math_level) then
	  r := pgmapcss_parse_eval(content, i - current_length, j, t);

	  i := i + r.text_length - current_length - 2;
	  a := cast(r.result as text[]);


	  if array_upper(param, 1) > 1 then
	    a := array_prepend(param[array_upper(param, 1)], a);
            a := array_prepend('o:' || t, a);
	    param := param[1:array_upper(param, 1)-1];
	    param := array_append(param, cast(a as text));

	  else
	    param := array_append(param, cast(array_prepend('o:' || t, a) as text));
	  end if;

	elsif math_level = 0 then
	  if current = '' then
	    r := pgmapcss_parse_eval(content, i + 1, j, t);
	    i := i + r.text_length - 1;

	    if array_upper(param, 1) = 1 then
	      a := array_prepend('o:' || t, param);
	      a := array_cat(a, cast(r.result as text[]));
	      param := a;
	    else
	      a := Array['o:' || t, cast(param as text)];
	      a := array_cat(a, cast(r.result as text[]));
	      param := a;
	    end if;

	  else
	    r := pgmapcss_parse_eval(content, i - current_length, j, t);
	    i := i - current_length + r.text_length - 2;
	    current := '';
	    current_whitespace := '';
	    current_length := 0;

	    a := cast(r.result as text[]);
	    a := array_prepend('o:'||t, a);
	    param := array_append(param, cast(a as text));
	  end if;
	else
	  if current != '' then
	    param := array_append(param, 'v:' || current);
	  end if;

	  ret.result := param;
	  ret.text_length := i;

	  return ret;
	end if;

	current := '';
	current_whitespace := '';
	current_length := 0;
      else
	-- maybe ignore whitespace
	if substring(content, i) ~ '^\s' then
	  -- ignore whitespace at beginning of token
	  if mode != 0 then
	    current_whitespace := current_whitespace || substring(content, i, 1);
	    current_length := current_length + 1;
	  end if;
	elsif mode > 1 then
	  raise warning 'Error parsing eval statement at "%..."', substring(content, i, 20);
	else
	  current := current || current_whitespace || substring(content, i, 1);
	  current_whitespace := '';
	  current_length := current_length + 1;
	  mode = 1;
	end if;
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
