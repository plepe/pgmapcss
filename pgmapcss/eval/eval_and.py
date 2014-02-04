def eval_and(param):
  for p in param:
      if eval_boolean([p]) == 'false':
          return 'false'

  return 'true'

# TESTS
# IN [ 'true', 'true' ]
# OUT 'true'
# IN [ 'true', 'false' ]
# OUT 'false'
# IN [ 'false', 'true' ]
# OUT 'false'
# IN [ 'false', 'false' ]
# OUT 'false'
