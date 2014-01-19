def eval_or(param):
    for p in param:
        if eval_boolean([p]) == 'true':
            return 'true'

    return 'false'
