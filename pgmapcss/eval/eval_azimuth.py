class config_eval_azimuth(config_base):
    mutable = 2

def eval_azimuth(param):
    if len(param) < 2:
        return ''

    if param[0] is None or param[0] == '' or param[1] is None or param[1] == '':
        return ''

    try:
        plan = plpy.prepare('select ST_Azimuth($1, $2) as r', ['geometry', 'geometry'])
        res = plpy.execute(plan, param)
    except Exception as err:
        debug('Eval::azimuth({}): Exception: {}'.format(param, err))
        return ''

    if res[0]['r'] is None:
      return ''

    return float_to_str(FROM_RADIANS(res[0]['r']))

# TESTS
# IN ['010100002031BF0D0033333333F4EE2F41E17A14DE3A8A5641', '010100002031BF0D0052B81E8583EF2F417B14AE77FC895641']
# OUT '163.98126146808423'

# IN [ '010100002031BF0D001E313E43A43B3A41F14D01FAA2B55641', '010100002031BF0D00860A74D2AE3B3A4172699C009CB55641' ]
# OUT '159.26747788922933'
# IN [ '010100002031BF0D00087417C6863B3A41DD362CA1ABB55641', '010100002031BF0D007B14AE078B3B3A4148E17A84B3B55641' ]
# OUT '7.682612875188862'
