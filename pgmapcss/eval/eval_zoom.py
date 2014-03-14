class config_eval_zoom(config_base):
    mutable = 3

    def possible_values(self, param_values, stat):
        return { '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20' }

def eval_zoom(param):
  import math

  return float_to_str(math.ceil(math.log(3.93216e+08 / render_context['scale_denominator'], 2)))

# TESTS
# IN []
# OUT '16'
