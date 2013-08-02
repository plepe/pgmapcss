drop function if exists pgmapcss_parse_comments(text);
create or replace function pgmapcss_parse_comments(text) returns text
as $$
#variable_conflict use_variable
declare
  m text;
  content text;
begin
  content := $1;

  loop
    m := substring(content from E'^\\s*(/\\*|//)');
    if m = '/*' then
      content := substring(content, strpos(content, '*/') + 2);
    elsif m = '//' then
      content := substring(content from E'\\s*//[^\n]*\n(.*)$');
    else
      return content;
    end if;
  end loop;

end;
$$ language 'plpgsql' immutable;


