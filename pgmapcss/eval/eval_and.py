class config_eval_and(config_base):
    math_level = 1
    op = '&&'
    mutable = 3

def eval_and(param, current):
  for p in param:
      if eval_boolean([p], current) == 'false':
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
