class config_eval_or(config_base):
    math_level = 1
    op = '||'
    mutable = 3

    def possible_values(self, param_values, prop, stat):
        if True in param_values:
            return ( { 'true', 'false' }, 3 )
        else:
            return config_base.possible_values(self, param_values, prop, stat)

def eval_or(param, current):
    for p in param:
        if eval_boolean([p], current) == 'true':
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
