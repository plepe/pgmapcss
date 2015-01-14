class config_eval_get(config_base):
    mutable = 3

def eval_get(param, current):
  if len(param) < 2:
      return ''

  i = eval_int([param[1]], current)

  if i == '':
      return ''

  i = int(i)
  if i < 0:
      return ''

  l = param[0].split(';')

  if i >= len(l):
      return ''

  return l[i]

# TESTS
# IN ['restaurant;bar', '-1']
# OUT ''
# IN ['restaurant;bar', '0']
# OUT 'restaurant'
# IN ['restaurant;bar', '1']
# OUT 'bar'
# IN ['restaurant;bar', '2']
# OUT ''
