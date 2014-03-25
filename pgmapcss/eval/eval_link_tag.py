class config_eval_link_tag(config_base):
    mutable = 0

def eval_link_tag(param):
    for p in param:
        if p in current['link_object']['tags']:
            return current['link_object']['tags'][p]

    return ''
