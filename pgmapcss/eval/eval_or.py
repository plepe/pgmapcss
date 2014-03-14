class config_eval_or(config_base):
    math_level = 1
    op = '||'
    mutable = 3

def eval_or(param):
    for p in param:
        if eval_boolean([p]) == 'true':
            return 'true'

    return 'false'

# TESTS
# IN [ 'true', 'true' ]
# OUT 'true'
# IN [ 'true', 'false' ]
# OUT 'true'
# IN [ 'false', 'true' ]
# OUT 'true'
# IN [ 'false', 'false' ]
# OUT 'false'
