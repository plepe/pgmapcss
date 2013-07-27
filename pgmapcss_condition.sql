create or replace function pgmapcss_condition(
  text
)
returns text
as $$
#variable_conflict use_variable
declare
  m text;
  ret text:=''::text;
  key text;
  op text;
  value text;
  condition text;
begin
  condition:=$1;

  if substring(condition, 1, 1)='!' then
    condition=substring(condition, 2);
    ret:=ret||'not ';
  end if;

  m = substring(condition from '^([a-zA-Z_0-9\-\:]+)(=|!=|<|>|<=|>=|\^=|\$=|\*=|~=|=~)(.*)$');
  if m is not null then
    key:=m;

    op = substring(condition from '^(?:[a-zA-Z_0-9\-\:]+)(=|!=|<|>|<=|>=|\^=|\$=|\*=|~=|=~)(.*)$');
    value = substring(condition from '^(?:[a-zA-Z_0-9\-\:]+)(?:=|!=|<|>|<=|>=|\^=|\$=|\*=|~=|=~)(.*)$');

    if op='=' then
      ret:=ret||'tags @> '''||quote_ident(key)||'=>'||quote_ident(value)||'''';
    elsif op='!=' then
      ret:=ret||'not tags @> '''||quote_ident(key)||'=>'||quote_ident(value)||'''';
    elsif op in ('<', '>', '<=', '>=') then
      ret:=ret||'cast(tags->'||quote_literal(key)||' as numeric) '||op||' '||quote_literal(value);
    elsif op='^=' then
      value:=value||'%';
      ret:=ret||'tags->'||quote_literal(key)||' similar to '||quote_literal(value);
    elsif op='$=' then
      value:='%'||value;
      ret:=ret||'tags->'||quote_literal(key)||' similar to '||quote_literal(value);
    elsif op='*=' then
      value:='%'||value||'%';
      ret:=ret||'tags->'||quote_literal(key)||' similar to '||quote_literal(value);
    elsif op='~=' then
      ret:=ret||quote_literal(value)||'=any(string_to_array(tags->'||quote_literal(key)||', '';''))';
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

      ret:=ret||'tags->'||quote_literal(key)||' '||op||' '||quote_literal(value);
    end if;

    return ret;
  end if;

  m = substring(condition from '^([a-zA-Z_0-9\-\:]+)$');
  if m is not null then
    ret:=ret||'tags ? '||quote_literal(m);

    return ret;
  end if;

  return null;
end;
$$ language 'plpgsql' immutable;
