class config_eval_to_dashes(config_base):
    pass

def eval_to_dashes(params):
    if len(params) == 0 or params[0] == '':
        return 'none'

    ret = params[0]

    if ret == 'none':
        return ret

    ret = str.replace(ret, ';', ',')
    ret = str.replace(ret, ' ', '')

    if len([
        t
        for t in ret.split(',')
        if not re.match('[0-9]+$', t)
    ]):
        # debug("invalid dashes value '{}'".format(params[0]))
        return 'none'

    return ret

# IN ['2,4']
# OUT '2,4'
# IN ['2; 4']
# OUT '2,4'
# IN ['20;40']
# OUT '20,40'
# IN ['20;;40']
# OUT 'none'
# IN ['none']
# OUT 'none'
# IN ['foo,5']
# OUT 'none'
