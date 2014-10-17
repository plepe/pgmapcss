class config_eval_debug(config_base):
    mutable = 0
    aliases = ( 'print', 'println' )

    def possible_values(self, param_values, prop, stat):
        return (param_values[0], 0)

def eval_debug(param, current):
    if len(param) == 1:
        plpy.warning(param[0])
    else:
        plpy.warning(param)

    return param[0]
