class config_eval_zoom(config_base):
    mutable = 3

    def possible_values(self, param_values, prop, stat):
        import math

        min_zoom = 0
        max_zoom = 20

        if 'statement' in prop and 'selector' in prop['statement']:
            if 'min_scale' in prop['statement']['selector'] and prop['statement']['selector']['min_scale'] > 0:
                max_zoom = int(math.ceil(math.log(3.93216e+08 / prop['statement']['selector']['min_scale'], 2)))
            if 'max_scale' in prop['statement']['selector'] and prop['statement']['selector']['max_scale'] is not None:
                min_zoom = int(math.ceil(math.log(3.93216e+08 / (prop['statement']['selector']['max_scale'] - 0.1), 2)))

        return { str(i) for i in range(min_zoom, max_zoom + 1) }

def eval_zoom(param):
  import math

  return float_to_str(math.ceil(math.log(3.93216e+08 / render_context['scale_denominator'], 2)))

# TESTS
# IN []
# OUT '16'
