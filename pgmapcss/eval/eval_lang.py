class config_eval_lang(config_base):
    mutable = 2

def eval_lang(param):
    if 'lang' in parameters:
        return parameters['lang']

    return 'en'
