drop table if exists eval_operators;
create table eval_operators (
  op		text		not null,
  func		text		not null,
  math_level	int		not null default 0,
  primary key(op)
);

create or replace function eval_TEMPLATE(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
begin
end;
$$ language 'plpgsql' immutable;
