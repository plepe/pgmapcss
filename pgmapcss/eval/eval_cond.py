class config_eval_cond(config_base):
    mutable = 3

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
