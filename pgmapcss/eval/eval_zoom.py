def eval_zoom(param):
  import math

  return math.ceil(math.log(3.93216e+08 / render_context['scale_denominator'], 2))

# TESTS
# IN []
# OUT '16'
