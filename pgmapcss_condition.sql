drop type if exists pgmapcss_condition_return cascade;
create type pgmapcss_condition_return as (
  result	text,
  text_length	int
);

drop function if exists pgmapcss_condition(text);
create or replace function pgmapcss_condition(
  text
)
returns pgmapcss_condition_return
as $$
#variable_conflict use_variable
declare
  m text;
  ret pgmapcss_condition_return;
  key text;
  op text;
  value text;
  content text;
  r record;
begin
  content:=$1;
  ret.result := ''::text;
  ret.text_length := 0;

  if substring(content, 1, 1)='!' then
    content=substring(content, 2);
    ret.result:=ret.result||'not ';
  end if;

  r := pgmapcss_parse_string(content, E'^([a-zA-Z_0-9\\-:]+)(=|!=|<|>|<=|>=|\\^=|\\$=|\\*=|~=|=~)');
  if r.result is not null then
    key := r.result;
    ret.text_length = ret.text_length + r.text_length;
    content = substring(content, r.text_length + 1);

    op = substring(content from '^(=|!=|<|>|<=|>=|\^=|\$=|\*=|~=|=~)(.*)$');
    ret.text_length = ret.text_length + length(op);
    content = substring(content, length(op) + 1);

    r := pgmapcss_parse_string(content, E'^([^\\]]+)\\]');
    value := r.result;
    ret.text_length = ret.text_length + r.text_length;
    content = substring(content, r.text_length + 1);

    if op='=' then
      ret.result:=ret.result||'tags @> '''||quote_ident(key)||'=>'||quote_ident(value)||'''';
    elsif op='!=' then
      ret.result:=ret.result||'not tags @> '''||quote_ident(key)||'=>'||quote_ident(value)||'''';
    elsif op in ('<', '>', '<=', '>=') then
      ret.result:=ret.result||'cast(tags->'||quote_literal(key)||' as numeric) '||op||' '||quote_literal(value);
    elsif op='^=' then
      value:=value||'%';
      ret.result:=ret.result||'tags->'||quote_literal(key)||' similar to '||quote_literal(value);
    elsif op='$=' then
      value:='%'||value;
      ret.result:=ret.result||'tags->'||quote_literal(key)||' similar to '||quote_literal(value);
    elsif op='*=' then
      value:='%'||value||'%';
      ret.result:=ret.result||'tags->'||quote_literal(key)||' similar to '||quote_literal(value);
    elsif op='~=' then
      ret.result:=ret.result||quote_literal(value)||'=any(string_to_array(tags->'||quote_literal(key)||', '';''))';
    elsif op='=~' then
      op='~';

      if value ~ '^/(.*)/$' then
        m=substring(value from '^/(.*)/$');
        if m is not null then
          value=m;
          op='~';
        end if;

      elsif value ~ '^/(.*)/i$' then
        m=substring(value from '^/(.*)/i$');
        if m is not null then
          value=m;
          op='~*';
        end if;
      end if;

      ret.result:=ret.result||'tags->'||quote_literal(key)||' '||op||' '||quote_literal(value);
    end if;

    return ret;
  end if;

  r := pgmapcss_parse_string(content, E'^([a-zA-Z_0-9\\-\\:]+)\\]');
  if r.result is not null then
    ret.result := ret.result||'tags ? '||quote_literal(r.result);
    ret.text_length := r.text_length;

    return ret;
  end if;

  ret.result := null;
  ret.text_length := 0;
  return ret;
end;
$$ language 'plpgsql' immutable;
