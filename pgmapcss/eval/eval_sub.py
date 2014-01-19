def eval_sub(param):
  ret = None

  for p in param:
      if p == '' or p == None:
          f = ''
      else:
          f = eval_metric([p])

      f = float(f) if f != '' else 0.0

      if ret is None:
          ret = f
      else:
          ret = ret - f

  return ret
