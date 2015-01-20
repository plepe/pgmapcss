class config_eval_is_closed(config_base):
    def possible_values(self, param_values, prop, stat):
        result = config_base.possible_values(self, param_values, prop, stat)
        eval_options = {}
        if len(result) > 2:
            eval_options = result[2]

        if len(param_values) == 0:
            if 'requirements' in eval_options:
                eval_options['requirements'].add('geo')
            else:
                eval_options['requirements'] = { 'geo' }

        return result[0], result[1], eval_options

def eval_is_closed(param, current):
    if len(param) > 0:
        geo = param[0]

    else:
        if 'geo' in current['properties'][current['pseudo_element']]:
            geo = current['properties'][current['pseudo_element']]['geo']
        else:
            geo = current['object']['geo']

    try:
        plan = plpy.prepare('select ST_GeometryType($1) in (\'ST_Polygon\', \'ST_MultiPolygon\') or (ST_GeometryType($1) in (\'ST_Line\') and ST_Line_Interpolate_Point($1, 0.0) = ST_Line_Interpolate_Point($1, 1.0)) as r', ['geometry'])
        res = plpy.execute(plan, [ geo ])
    except Exception as err:
        debug('Eval::is_closed({}): Exception: {}'.format(param, err))
        return ''

    return 'true' if res[0]['r'] else 'false'
