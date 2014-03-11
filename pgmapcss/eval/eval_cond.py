class config_eval_cond(config_base):
    def compiler(self, param, eval_param, stat):
        ret = '(' + param[1] + ' if eval_boolean([' + param[0] + ']' + eval_param + ') == \'true\''
        if len(param) > 2:
            ret += ' else ' + param[2]
        else:
            ret += " else ''"
        ret += ')'
        return ret
