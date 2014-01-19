def eval_buffer(param):
    pass
#create or replace function eval_buffer(param text[],
#  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
#returns text
#as $$
##variable_conflict use_variable
#declare
#  t text;
#begin
#  if array_upper(param, 1) < 2 then
#    return param[1];
#  end if;
#
#  t := eval_metric(Array[param[2], 'u'], object, current, render_context);
#
#  if t is null or t = '' then
#    return param[1];
#  end if;
#
#  return ST_Buffer(param[1], cast(t as float));
#end;
#$$ language 'plpgsql' immutable;
