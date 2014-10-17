class config_eval_sqrt(config_base):
    def mutable(self, param_values, stat):
        import pgmapcss.eval
        config_metric = pgmapcss.eval.eval_functions.list()['metric']
        ret = [ config_metric.mutable([p], stat) for p in param_values ]
        return min(ret)

def eval_sqrt(param, current):
    if len(param) == 0:
        return ''

    f = eval_metric([param[0]], current)
    if f == '':
        return ''

    f = float(f)

    if f < 0:
        return ''

    f = math.sqrt(f)

    return float_to_str(f)

# TESTS
# IN ['4']
# OUT '2'
# IN ['2']
# OUT '1.4142135623730951'
# IN ['1']
# OUT '1'
# IN ['-2']
# OUT ''
# IN ['0']
# OUT '0'
