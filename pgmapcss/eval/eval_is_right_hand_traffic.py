class config_eval_is_right_hand_traffic(config_base):
    mutable = 1

def eval_is_right_hand_traffic(param):
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

# Tests
# IN ['010100002031BF0D00A4703D0A77E5C9407B14AE5750155A41', 'force']
# OUT 'false'
# IN ['010100002031BF0D0033333333F4EE2F41E17A14DE3A8A5641', 'force']
# OUT 'true'
# IN ['010300002031BF0D0001000000050000000000000000685DC0000000E00DAA4F410000000000685DC00000008020795E41000000800E984F410000008020795E41000000800E984F41000000E00DAA4F410000000000685DC0000000E00DAA4F41', 'force']
# OUT 'partly'
