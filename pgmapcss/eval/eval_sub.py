class config_eval_sub(config_base):
    math_level = 1
    op = '-'
    def mutable(self, param_values, stat):
        import pgmapcss.eval
        config_metric = pgmapcss.eval.eval_functions.list()['metric']
        ret = [ config_metric.mutable([p], stat) for p in param_values ]
        return min(ret)

def eval_sub(param, current):
  ret = None

  for p in param:
      if p == '' or p == None:
          f = ''
      else:
          f = eval_metric([p], current)

      f = float(f) if f != '' else 0.0

      if ret is None:
          ret = f
      else:
          ret = ret - f

  return float_to_str(ret)

# TESTS
# IN ['4', '2', '2']
# OUT '0'
# IN ['5.6', '2.3']
# OUT '3.3'
# IN ['3', '5.0']
# OUT '-2'
