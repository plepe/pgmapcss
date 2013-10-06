-- parse a tree from an eval statement. Returns the tree and the length that was read from the content.
create or replace function pgmapcss_parse_eval(
  			text,
  "offset"		int default 1,
			int default 0,
			text default null,
  OUT result text,
  OUT content text
)
as $$
#variable_conflict use_variable
declare
  esc boolean := false;
  i int;
  j int;
  t text;
  r record;
  a text[];
  b text[];
  current text;
  current_result text[];
  current_length int;
  current_whitespace text;
  current_op text;
  math_level int;
  param text[];
  mode int := 0;
  last_mode int;
  last_content text;
  -- 0 .. reading whitespace before token
  -- 1 .. reading token
  -- 2 .. token finished, read quoted string
  -- 3 .. token finished (e.g. after brackets)
  op_regexp text;
  op_math_level hstore;
begin
  content := substring($1, "offset");
  -- raise notice 'parse_eval(''%'', %, ''%'')', content, math_level, current_op;
  
  -- compile eval operator regexp
  select '^(' || array_to_string(array_agg(x), '|') || ')' into op_regexp from (select replace(regexp_replace(op, '([\?\.\+\*\^\$\\])', E'\\ \\1', 'g'), ' ', '') x from eval_operators) t;
  select hstore(array_agg(op), array_agg(cast(eval_operators.math_level as text))) into op_math_level from eval_operators;

  i := 1;
  current := ''::text;
  current_length := 0;
  param := Array[]::text[];
  current_result := Array[]::text[];

  math_level := $3;
  current_op := $4;

  loop
    -- make sure to break on parsing errors
    if content = last_content and mode = last_mode then
      raise exception 'Error parsing eval(...) at "%"', substring(content, 1, 20);
    end if;
    last_content := content;
    last_mode := mode;

    -- raise notice 'eval: (math%) (mode%) "%..."', math_level, mode, substring(content, i, 20);

    if mode = 0 then
      -- whitespace
      if content ~ '^\s+' then
	content := substring(content from '^\s+(.*)$');

      -- a number, opt. with unit
      elsif content ~ '^[\-\+]?[0-9]+(\.[0-9]+)?([Ee][\-\+][0-9]+)?(\s*(%|px|m|u))?' then
        current_result := array_append(current_result,
	  'v:' || substring(content from '^([\-\+]?[0-9]+(\.[0-9]+)?([Ee][\-\+][0-9]+)?(\s*(%|px|m|u))?)'));
	content := substring(content from '^[\-\+]?[0-9]+(?:\.[0-9]+)?(?:[Ee][\-\+][0-9]+)?(?:\s*(?:%|px|m|u))?(.*)$');
        mode := 20;

      -- an identifier
      elsif content ~ '^[a-zA-Z_:][a-zA-Z_:0-9]*' then
        current := substring(content from '^([a-zA-Z_:][a-zA-Z_:0-9]*)');
	content := substring(content from '^[a-zA-Z_:][a-zA-Z_:0-9]*(.*)$');
        mode := 10;

      -- opening bracket
      elsif content ~ '^\(' then
        content := substring(content, 2);
	r := pgmapcss_parse_eval(content);
	current_result := array_append(current_result,
	  r.result);
	content := r.content;

	mode := 1;
      
      -- closing bracket, ',' or ';'
      elsif content ~ '^(\)|,|;)' then
        result := null;

	return;

      -- quoted string
      elsif content ~ '^["'']' then
        r := pgmapcss_parse_string(content);
        current_result := array_append(current_result, 'v:' || r.result);
	content := r.content;

	mode := 20;

      end if;

    elsif mode = 1 then
      -- whitespace
      if content ~ '^\s+' then
	content := substring(content from '^\s+(.*)$');

      elsif content ~ '^\)' then
        content := substring(content, 2);
	mode := 20;

      end if;

    -- read an identifier, this could be a function call
    elsif mode = 10 then
      -- it is a function call
      if content ~ '^\(' then
	content := substring(content, 2);
	current_result := array_append(current_result, 'f:' || current);

	if content ~ '^\s*\)' then
	  content := substring(content from '^\s*\)(.*)$');
	  
	  mode := 20;

	else
	  r := pgmapcss_parse_eval(content);
	  current_result := array_append(current_result, r.result);
	  content := r.content;

	  mode := 11;
	end if;

      else
	current_result := array_append(current_result, 'v:' || current);
	mode := 20;

      end if;

    -- inbetween a function call
    elsif mode = 11 then
      if content ~ '^\s*[,;]' then
	content := substring(content from '^\s*[,;](.*)$');

	r := pgmapcss_parse_eval(content);
	current_result := array_append(current_result, r.result);
	content := r.content;

      elsif content ~ '^\s*\)' then
	content := substring(content from '^\s*\)(.*)$');

	mode := 20;

      end if;

    -- now we are awaiting an operator - or return
    elsif mode = 20 then
      if content ~ '^\s+' then
	content := substring(content from '^\s+(.*)$');

      elsif content ~ '^(\)|,|;)' or content = '' then
	if array_upper(current_result, 1) = 1 then
	  result := current_result[1];
	else
	  result := cast(current_result as text);
	end if;

	return;

      elsif content ~ op_regexp then
	current := substring(content from op_regexp);

	j := cast(op_math_level->current as int);

	if j > math_level then
	  content := substring(content, length(current) + 1);

	  current_op := current;
	  math_level := j;

	  if array_upper(current_result, 1) = 1 then
	    current_result := Array[ 'o:' || current_op,
	      current_result[1] ];
	  else
	    current_result := Array[ 'o:' || current_op,
	      cast(current_result as text) ];
	  end if;

	  r := pgmapcss_parse_eval(content, 1, math_level, current_op);
	  current_result := array_append(current_result, r.result);
	  content := r.content;

	  mode := 21;
        else
	  if array_upper(current_result, 1) = 1 then
	    result := current_result[1];
	  else
	    result := cast(current_result as text);
	  end if;

	  return;
	end if;

      end if;

    elsif mode = 21 then
      if content ~ '^\s+' then
	content := substring(content from '^\s+(.*)$');

      elsif content ~ '^(\)|,|;)' or content = '' then
	if array_upper(current_result, 1) = 1 then
	  result := current_result[1];
	else
	  result := cast(current_result as text);
	end if;

	return;

      elsif content ~ op_regexp then
	current := substring(content from op_regexp);

	if current = current_op then
	  content := substring(content, length(current) + 1);

	  r := pgmapcss_parse_eval(content, 1, math_level, current_op);
	  current_result := array_append(current_result, r.result);
	  content := r.content;
	else
	  j := cast(op_math_level->current as int);

	  if j >= math_level then
	    content := substring(content, length(current) + 1);

	    current_op := current;
	    math_level := j;

	    if array_upper(current_result, 1) = 1 then
	      current_result := Array[ 'o:' || current_op,
		current_result[1] ];
	    else
	      current_result := Array[ 'o:' || current_op,
		cast(current_result as text) ];
	    end if;

	    r := pgmapcss_parse_eval(content, 1, math_level, current_op);
	    current_result := array_append(current_result, r.result);
	    content := r.content;

	  else
	    if array_upper(current_result, 1) = 1 then
	      result := current_result[1];
	    else
	      result := cast(current_result as text);
	    end if;

	    return;

	  end if;

	end if;

      end if;
    end if;
  end loop;
end;
$$ language 'plpgsql' immutable;
