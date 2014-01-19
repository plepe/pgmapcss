def eval_and(param):
  for p in param:
      if eval_boolean([p]) == 'false':
          return 'false'

  return 'true'
