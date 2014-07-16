class config_eval_righthandtraffic(config_base):
    mutable = 1

def eval_righthandtraffic(param):
    if len(param) > 0:
        geo = param[0]
    else:
        geo = current['properties'][current['pseudo_element']]['geo']

    plan = plpy.prepare('select ST_Within($1, geo) as r from _pgmapcss_left_right_hand_traffic where ST_Intersects($1, geo)', ['geometry'])
    res = plpy.execute(plan, [ geo ])


    if len(res) == 0:
        return 'true'

    if False in [row['r'] for row in res]:
        return 'partly'

    return 'false'
