class config_eval_parameter(config_base):
    mutable = 2

def eval_parameter(param, current):
    if len(param) == 0:
        return ''

    if param[0] in parameters:
        return parameters[param[0]]

    return ''
