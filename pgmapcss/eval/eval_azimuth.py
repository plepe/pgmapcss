def eval_azimuth(param):
  if len(param) < 2:
      return ''

  if param[0] is None or param[0] == '' or param[1] is None or param[1] == '':
      return ''

  plan = plpy.prepare('select degrees(ST_Azimuth($1, $2)) as r', ['geometry', 'geometry'])
  res = plpy.execute(plan, param)

  return float_to_str(res[0]['r'])

# TESTS
# IN ['010100002031BF0D0033333333F4EE2F41E17A14DE3A8A5641', '010100002031BF0D0052B81E8583EF2F417B14AE77FC895641']
# OUT '163.98126146808423'
