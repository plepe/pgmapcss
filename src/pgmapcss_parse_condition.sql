drop function if exists pgmapcss_parse_condition(text);
create or replace function pgmapcss_parse_condition(
  text
)
returns pgmapcss_condition
as $$
#variable_conflict use_variable
declare
  m text;
  ret pgmapcss_condition;
  content text;
  r record;
begin
  content:=$1;
  ret.content := null;
  ret.op := '';

  if substring(content, 1, 1)='!' then
    content=substring(content, 2);
    ret.op := ret.op || '! ';
  end if;

  r := pgmapcss_parse_string(content, E'^([a-zA-Z_0-9\\-:]+)(=|!=|<|>|<=|>=|\\^=|\\$=|\\*=|~=|=~)');
  if r.result is not null then
    ret.key := r.result;
    content = r.content;

    ret.op = ret.op || substring(content from '^(=|!=|<|>|<=|>=|\^=|\$=|\*=|~=|=~)(.*)$');
    content = substring(content, length(ret.op) + 1);

    r := pgmapcss_parse_string(content, E'^eval\\(');
    if r is not null then
      r := pgmapcss_parse_eval(content, 6);
      ret.value := r.result;
      ret.value_type := 1;
      content = r.content;
    else
      r := pgmapcss_parse_string(content, E'^([^\\]]+)\\]');
      ret.value := r.result;
      ret.value_type := 0;
      content = r.content;
    end if;

    ret.content := content;
    return ret;
  end if;

  r := pgmapcss_parse_string(content, E'^([a-zA-Z_0-9\\-\\:]+)\\]');
  if r.result is not null then
    ret.op := ret.op || 'has_tag';
    ret.key := r.result;
    ret.value := null;
    ret.content := r.content;

    return ret;
  end if;

  ret.op := null;
  ret.content := null;
  return ret;
end;
$$ language 'plpgsql' immutable;
