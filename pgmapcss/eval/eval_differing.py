class config_eval_differing(config_base):
    def mutable(self, param_values, stat):
        import pgmapcss.eval
        config_metric = pgmapcss.eval.eval_functions.list()['metric']
        ret = [ config_metric.mutable([p], stat) for p in param_values ]
        return min(ret)

class config_eval_differing(config_base):
    math_level = 7
    op = ('!=', '<>')

def eval_differing(param):
    # empty parameter list -> all equal
    if len(param) == 0:
        return 'false'

    # identical comparison
    if len(param) != len(set(param)):
        return 'false'

    # convert all values to numbers
    values = [ eval_metric([v]) for v in param ]

    if not '' in values and len(values) != len(set(values)):
        return 'false'

    return 'true';

# TESTS
# IN ['5', '5']
# OUT 'false'
# IN ['5.0', '5', '3.00']
# OUT 'false'
# IN ['3', '5']
# OUT 'true'
# IN []
# OUT 'false'
# IN ['foo', 'bar']
# OUT 'true'
# IN ['foo', '5']
# OUT 'true'
# IN ['foo', 'foo']
# OUT 'false'
