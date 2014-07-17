class config_eval_righthandtraffic(config_base):
    mutable = 1

def eval_righthandtraffic(param):
    force = False
    if len(param) > 1:
        force = param[1] == 'force'

    if not force and not 'righthandtraffic' in render_context:
        render_context['righthandtraffic'] = None
        render_context['righthandtraffic'] = eval_righthandtraffic([render_context['bbox']])

    if not force and render_context['righthandtraffic'] not in ( None, 'partly' ) and not force:
        return render_context['righthandtraffic']

    if len(param) > 0:
        geo = param[0]
    else:
        geo = current['properties'][current['pseudo_element']]['geo']

    if not geo:
        return 'partly'

    plan = plpy.prepare('select ST_Within($1, geo) as r from _pgmapcss_left_right_hand_traffic where ST_Intersects($1, geo)', ['geometry'])
    res = plpy.execute(plan, [ geo ])


    if len(res) == 0:
        return 'true'

    if False in [row['r'] for row in res]:
        return 'partly'

    return 'false'
