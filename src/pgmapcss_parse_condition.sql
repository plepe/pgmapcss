drop function if exists pgmapcss_parse_condition(text);
create or replace function pgmapcss_parse_condition(
  IN text,
  OUT result pgmapcss_condition,
  OUT content text
)
as $$
#variable_conflict use_variable
declare
  m text;
  r record;
begin
  content:=$1;
  result.op := '';

  if substring(content, 1, 1)='!' then
    content=substring(content, 2);
    result.op := result.op || '! ';
  end if;

  r := pgmapcss_parse_string(content, E'^([a-zA-Z_0-9\\-\.:]+)(=|!=|<|>|<=|>=|\\^=|\\$=|\\*=|~=|=~)');
  if r.result is not null then
    result.key := r.result;
    content = r.content;

    result.op = result.op || substring(content from '^(=|!=|<|>|<=|>=|\^=|\$=|\*=|~=|=~)(.*)$');
    content = substring(content, length(result.op) + 1);

    r := pgmapcss_parse_string(content, E'^eval\\(');
    if r is not null then
      r := pgmapcss_parse_eval(content, 6);
      result.value := r.result;
      result.value_type := 1;
      content = r.content;
    else
      r := pgmapcss_parse_string(content, E'^([^\\]]+)\\]');
      result.value := r.result;
      result.value_type := 0;
      content = r.content;
    end if;

    return;
  end if;

  r := pgmapcss_parse_string(content, E'^([a-zA-Z_0-9\\-\.\\:]+)\\]');
  if r.result is not null then
    result.op := result.op || 'has_tag';
    result.key := r.result;
    result.value := null;
    content := r.content;

    return;
  end if;

  result.op := null;
  return;
end;
$$ language 'plpgsql' immutable;
