def eval_line_merge(param):
    pass
#create or replace function eval_line_merge(param text[],
#  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
#returns text
#as $$
##variable_conflict use_variable
#declare
#  t text;
#begin
#  if array_upper(param, 1) < 1 then
#    return '';
#  end if;
#
#  return ST_LineMerge(param[1]);
#end;
#$$ language 'plpgsql' immutable;
