class config_eval_boolean(config_base):
    mutable = 0

    def possible_values(self, param_values, prop, stat):
        return (param_values[0], 0)

def eval_debug(param):
    if len(param) == 1:
        plpy.notice(param[0])
    else:
        plpy.notice(param)

    return param[0]
