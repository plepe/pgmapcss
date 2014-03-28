class config_eval_ge(config_base):
    math_level = 7
    op = '>='
    def mutable(self, param_values, stat):
        import pgmapcss.eval
        config_metric = pgmapcss.eval.eval_functions.list()['metric']
        ret = [ config_metric.mutable([p], stat) for p in param_values ]
        return min(ret)

    def possible_values(self, param_values, prop, stat):
        if len(param_values) < 2:
            return ( '', self.mutable(param_values, stat) )

        if True in param_values:
            return ( { 'true', 'false' }, 3 )
        else:
            return config_base.possible_values(self, param_values, prop, stat)

def eval_ge(param):
    if len(param) < 2:
        return ''

    a = eval_metric(param[0:1])
    a = float(a) if a != '' else 0.0

    for p in param[1:]:
        b = eval_metric([p])
        b = float(b) if b != '' else 0.0

        if not a >= b:
            return 'false'

        a = b

    return 'true'

# TESTS
# IN ['1', '2']
# OUT 'false'
# IN ['2', '1']
# OUT 'true'
# IN ['1', '2', '3']
# OUT 'false'
# IN ['3', '2', '1']
# OUT 'true'
# IN ['1', '2', '2.0', '3']
# OUT 'false'
# IN ['3', '2', '2.0', '1']
# OUT 'true'
# IN ['1.0', '1']
# OUT 'true'
