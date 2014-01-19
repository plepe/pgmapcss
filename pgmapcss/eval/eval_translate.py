def eval_translate(param):
    pass
#create or replace function eval_translate(param text[],
#  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
#returns text
#as $$
##variable_conflict use_variable
#declare
#  x float;
#  y float;
#begin
#  if array_upper(param, 1) is null then
#    return '';
#  elsif array_upper(param, 1) < 3 then
#    return param[1];
#  end if;
#
#  x := eval_metric(Array[param[2], 'u'], object, current, render_context);
#  y := eval_metric(Array[param[3], 'u'], object, current, render_context);
#
#  return ST_Translate(param[1], x, y);
#end;
#$$ language 'plpgsql' immutable;
#
#
#
