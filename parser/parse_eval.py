import re
import db
from .parse_string import parse_string

eval_operators = None

def read_eval_operators():
    global eval_operators
    eval_operators = {}

    conn = db.connection()
    res = conn.prepare('select * from eval_operators')

    for elem in res():
        eval_operators[elem['op']] = elem

def parse_eval(to_parse, math_level=0, current_op=None, rek=0):
    if eval_operators == None:
        read_eval_operators()

    eval_op_regexp = '(' + '|'.join([re.sub(r'([\?\.\+\*\^\$\|\\])', r'\\\1', k) for k in eval_operators]) + ')'
    current = ''
    current_result = []
    mode = 0

    last_to_parse = None
    last_mode = None

    while True:
        # make sure to break on parsing errors
        if to_parse == last_to_parse and mode == last_mode:
            raise Exception('Error parsing eval(...) at "', to_parse[0:20], '"')

        last_to_parse = to_parse
        last_mode = mode

        # print('eval: (rek{}, math{}, mode{}) "{}..."'.format(rek, math_level, mode, to_parse[0:20]))

        if mode == 0:
            # whitespace
            if re.match('\s+', to_parse):
                to_parse = to_parse[len(re.match('\s+', to_parse).group(0)):]

            # a number, opt. with unit
            elif re.match('[\-\+]?[0-9]+(\.[0-9]+)?([Ee][\-\+][0-9]+)?(\s*(%|px|m|u))?', to_parse):
                m = re.match('[\-\+]?[0-9]+(\.[0-9]+)?([Ee][\-\+][0-9]+)?(\s*(%|px|m|u))?', to_parse)
                current_result.append('v:' + m.group(0))
                to_parse = to_parse[len(m.group(0)):]
                mode = 20

            # an identifier
            elif re.match('[a-zA-Z_:][a-zA-Z_:0-9]*', to_parse):
                m = re.match('[a-zA-Z_:][a-zA-Z_:0-9]*', to_parse)
                current = m.group(0)
                to_parse = to_parse[len(m.group(0)):]
                mode = 10

            # opening bracket
            elif re.match('\(', to_parse):
                (result, to_parse) = parse_eval(to_parse[1:], rek=rek+1)
                current_result.append(result)
                mode = 1

            # closing bracket, ',' or ';'
            elif re.match('(\)|,|;)', to_parse):
                return ( result, to_parse )

            # quoted string
            elif re.match('["\']', to_parse):
                r = parse_string(to_parse)
                current_result.append('v:' + r[0])
                to_parse = r[1]
                mode = 20

        elif mode == 1:
            # whitespace
            if re.match('\s+', to_parse):
                to_parse = to_parse[len(re.match('\s+', to_parse).group(0)):]

            elif re.match('\)', to_parse):
                to_parse = to_parse[1:]
                mode = 20

        # read an identifier, this could be a function call
        elif mode == 10:
            # it is a function call
            if re.match('\(', to_parse):
                to_parse = to_parse[1:]
                current_result.append('f:' + current)

                if re.match('\s*\)', to_parse):
                    m = re.match('\s*\)', to_parse)
                    to_parse = to_parse[len(m.group(0)):]
                    mode = 20

                else:
                    ( result, to_parse) = parse_eval(to_parse, rek=rek+1)
                    current_result.append(result)
                    mode = 11

            else:
                current_result.append('v:' + current)
                mode = 20

        # inbetween a function call
        elif mode == 11:
            if re.match('\s*[,;]', to_parse):
                m = re.match('\s*[,;]', to_parse)
                to_parse = to_parse[len(m.group(0)):]
                ( result, to_parse ) = parse_eval(to_parse, rek=rek+1)
                current_result.append(result)

            elif re.match('\s*\)', to_parse):
                m = re.match('\s*\)', to_parse)
                to_parse = to_parse[len(m.group(0)):]
                mode = 20

        # now we are awaiting an operator - or return
        elif mode == 20:
            if re.match('\s+', to_parse):
                to_parse = to_parse[len(re.match('\s+', to_parse).group(0)):]

            elif re.match('^(\)|,|;)', to_parse) or to_parse == '':
                if len(current_result) == 1:
                    return ( current_result[0], to_parse )
                else:
                    return ( current_result, to_parse )

            elif re.match(eval_op_regexp, to_parse):
                m = re.match(eval_op_regexp, to_parse)
                current = m.group(1)

                j = int(eval_operators[current]['math_level'])

                if j > math_level:
                    to_parse = to_parse[len(m.group(0)):]

                    current_op = current
                    math_level = j

                    if len(current_result) == 1:
                        current_result = [ 'o:' + current_op, current_result[0] ]
                    else:
                        current_result = [ 'o:' + current_op, current_result ]

                    ( result, to_parse ) = parse_eval(to_parse, math_level, current_op, rek=rek+1)
                    current_result.append(result)
                    mode = 21

                else:
                    if len(current_result) == 1:
                      return ( current_result[0], to_parse )
                    else:
                      return ( current_result, to_parse)

        elif mode == 21:
            if re.match('\s+', to_parse):
                to_parse = to_parse[len(re.match('\s+', to_parse).group(0)):]

            elif re.match('(\)|,|;)', to_parse) or to_parse == '':
              if len(current_result) == 1:
                  return ( current_result[0], to_parse )
              else:
                  return ( current_result, to_parse )

            elif re.match(eval_op_regexp, to_parse):
                m = re.match(eval_op_regexp, to_parse)
                current = m.group(1)

                if current == current_op:
                      to_parse = to_parse[len(m.group(0)):]

                      ( result, to_parse ) = parse_eval(to_parse, math_level, current_op, rek=rek+1)
                      current_result.append(result)

                else:
                  j = int(eval_operators[current]['math_level'])

                  if j >= math_level or rek == 0:
                      to_parse = to_parse[len(m.group(0)):]

                      current_op = current
                      math_level = j

                      if len(current_result) == 1:
                        current_result = [ 'o:' + current_op, current_result[0] ]
                      else:
                        current_result = [ 'o:' + current_op, current_result ]

                      ( result, to_parse ) = parse_eval(to_parse, math_level, current_op, rek=rek+1)
                      current_result.append(result)

                  else:
                      if len(current_result) == 1:
                        return ( current_result[0], to_parse )
                      else:
                        return ( current_result, to_parse )
