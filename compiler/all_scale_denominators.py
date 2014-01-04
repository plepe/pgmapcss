def all_scale_denominators(stat):
    return sorted(list(set([
            v['selectors']['min_scale']
            for v in stat['statements']
        ] + \
        [
            v['selectors']['max_scale']
            for v in stat['statements']
            if v['selectors']['max_scale'] != None
        ])),
        reverse=True)
