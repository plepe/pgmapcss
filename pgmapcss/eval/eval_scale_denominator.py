class config_eval_scale_denominator(config_base):
    mutable = 2

def eval_scale_denominator(param):
    return float_to_str(render_context['scale_denominator'])

# TESTS
# IN []
# OUT '8536.77'
