class config_is_closed(config_base):
    mutable = 1

def eval_is_closed(param, current):
    if len(param) > 0:
        geo = param[0]

    else:
        if 'geo' in current['properties'][current['pseudo_element']]:
            geo = current['properties'][current['pseudo_element']]['geo']
        else:
            geo = current['object']['geo']

    plan = plpy.prepare('select ST_GeometryType($1) in (\'ST_Polygon\', \'ST_MultiPolygon\') or (ST_GeometryType($1) in (\'ST_Line\') and ST_Line_Interpolate_Point($1, 0.0) = ST_Line_Interpolate_Point($1, 1.0)) as r', ['geometry'])
    res = plpy.execute(plan, [ geo ])

    return 'true' if res[0]['r'] else 'false'
