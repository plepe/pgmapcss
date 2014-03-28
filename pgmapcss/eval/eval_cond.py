class config_eval_cond(config_base):
    mutable = 3

    def possible_values(self, param_values, prop, stat):
        if param_values[0] is not True:
            return config_base.possible_values(self, param_values, prop, stat)

        if len(param_values) > 2:
            return ({ param_values[1], param_values[2] }, 3)
        else:
            return ({ param_values[1], '' }, 3)

    def compiler(self, param, eval_param, stat):
        ret = '(' + param[1] + ' if eval_boolean([' + param[0] + ']' + eval_param + ') == \'true\''
        if len(param) > 2:
            ret += ' else ' + param[2]
        else:
            ret += " else ''"
        ret += ')'
        return ret

# IN [ 'true', 'A' ]
# OUT 'A'
# IN [ 'true', 'A', 'B' ]
# OUT 'A'
# IN [ 'false', 'A' ]
# OUT ''
# IN [ 'false', 'A', 'B' ]
# OUT 'B'
# IN [ '0', 'A', 'B' ]
# OUT 'B'
# IN [ 'no', 'A', 'B' ]
# OUT 'B'
# IN [ '', 'A', 'B' ]
# OUT 'B'
# IN [ 'foo', 'A', 'B' ]
# OUT 'A'
# IN [ 'bar', 'A', 'B' ]
# OUT 'A'
