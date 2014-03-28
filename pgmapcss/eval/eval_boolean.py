class config_eval_boolean(config_base):
    mutable = 3

    def possible_values(self, param_values, prop, stat):
        if len(param_values) == 0:
            return ( '', 3 )

        if param_values[0] is True:
            return ( { 'true', 'false' }, 3 )
        else:
            return config_base.possible_values(self, param_values, prop, stat)

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
