def eval_parent_tag(param, current):
    for p in param:
        if p in current['parent_object']['tags']:
            return current['parent_object']['tags'][p]

    return ''
