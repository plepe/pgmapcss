class config_eval_boolean(config_base):
    mutable = 3

def eval_boolean(param):
    if len(param) == 0:
        return ''

    if param[0] is None or\
        param[0].strip() in ('', 'no', 'false') or\
        re.match('[\-\+]?0+(\.0+)?$', param[0]):
            return 'false'

    return 'true'

# TESTS
# IN ['1']
# OUT 'true'
# IN ['0']
# OUT 'false'
# IN ['']
# OUT 'false'
# IN ['no']
# OUT 'false'
# IN ['yes']
# OUT 'true'
# IN ['foo']
# OUT 'true'
# IN []
# OUT ''
