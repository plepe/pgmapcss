class config_eval_power(config_base):
    def mutable(self, param_values, stat):
        import pgmapcss.eval
        config_metric = pgmapcss.eval.eval_functions.list()['metric']
        ret = [ config_metric.mutable([p], stat) for p in param_values ]
        return min(ret)

def eval_power(param):
    if len(param) < 2:
        return ''

    f1 = eval_metric(param[0:1])
    f2 = eval_metric(param[1:2])

    f1 = float(f1) if f1 != '' else 0.0
    f2 = float(f2) if f2 != '' else 0.0

    return float_to_str(f1 ** f2)

# TESTS
# IN ['2', '3']
# OUT '8'
# IN ['2', '0.5']
# OUT '1.4142135623730951'
# IN ['5', '1']
# OUT '5'
# IN ['5', '0']
# OUT '1'
