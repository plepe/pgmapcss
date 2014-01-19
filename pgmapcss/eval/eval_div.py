def eval_div(param):
  ret = None

  for p in param:
      if p == '' or p == None:
          f = ''
      else:
          f = eval_metric([p])

      f = float(f) if f != '' else 0.0

      if ret is None:
          ret = f
      elif f == 0:
          return ''
      else:
          ret = ret / f

  return '%G' % ret

# TESTS
# IN ['5', '1']
# OUT '5'
# IN ['5', '2']
# OUT '2.5'
# IN ['5', '0']
# OUT ''
# IN ['-5', '2']
# OUT '-2.5'
# IN ['6', '4', '2']
# OUT '0.75'
