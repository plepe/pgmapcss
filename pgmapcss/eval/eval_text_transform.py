def eval_text_transform(param):
    return param[0]
#create or replace function eval_text_transform(param text[],
#  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
#returns text
#as $$
##variable_conflict use_variable
#declare
#begin
#  if array_upper(param, 1) is null then
#    return null;
#  end if;
#  
#  if array_upper(param, 1) = 1 then
#    return param[1];
#  end if;
#
#  return (CASE
#    WHEN param[2] = 'none' THEN param[1]
#    WHEN param[2] = 'uppercase' THEN upper(param[1])
#    WHEN param[2] = 'lowercase' THEN lower(param[1])
#    WHEN param[2] = 'capitalize' THEN (select array_to_string(array_agg(v), ' ') from (select upper(substring(v, 1, 1)) || lower(substring(v, 2)) v from (select unnest(string_to_array('foo bar Test bLA', ' ')) v) t) t)
#    ELSE param[1]
#  END);
#end;
#$$ language 'plpgsql' immutable;
#
