class config_eval_parent_geo(config_base):
    eval_options = {
        'requirements': { 'parent_geo' }
    }

def eval_parent_geo(param, current):
    return current['parent_object']['geo']
