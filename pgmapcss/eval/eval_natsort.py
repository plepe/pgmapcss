def eval_natsort(param):
    """ Sort the given list in the way that humans expect.
from: http://www.codinghorror.com/blog/2007/12/sorting-for-humans-natural-sort-order.html
    """
    if len(param) == 0:
        return ""

    if len(param) == 1:
        param = param[0].split(';')

    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    param.sort( key=alphanum_key )

    return ';'.join(param)

# TESTS
# IN ['1;103;2;13;14;102;3']
# OUT '1;2;3;13;14;102;103'
# IN ['1A;2A;3A;A1;A20;A3;A104;ABC1;ABC123;ABC1A']
# OUT '1A;2A;3A;A1;A3;A20;A104;ABC1;ABC1A;ABC123'
# IN ['1', 'B', 'A', '2']
# OUT '1;2;A;B'
