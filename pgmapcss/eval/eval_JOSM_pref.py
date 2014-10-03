class config_eval_JOSM_pref(config_base):
    mutable = 3

def eval_JOSM_pref(param):
    if len(param) < 2:
        return ''

    return param[1]
