def eval_azimuth(param):
  if len(param) < 2:
      return ''

  if param[0] is None or param[0] == '' or param[1] is None or param[1] == '':
      return ''

  plan = plpy.prepare('select degrees(ST_Azimuth($1, $2)) as r', ['geometry', 'geometry'])
  res = plpy.execute(plan, param)

  return res[0]['r']
