def eval_boolean(param):
    if len(param) == 0:
        return ''

    if param[0] is None or\
        param[0].strip() in ('', 'no', 'false') or\
        re.match('[\-\+]?0+(\.0+)?$', param[0]):
            return 'false'

    return 'true'
