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
        if to_parse.pos() == last_to_parse and mode == last_mode:
            raise Exception('Error parsing eval(...) at')

        last_to_parse = to_parse.pos()
        last_mode = mode

        # print('eval: (rek{}, math{}, mode{}) "{}..."'.format(rek, math_level, mode, to_parse[0:20]))

        if mode == 0:
            # whitespace
            if to_parse.match('\s+'):
                pass

            # a number, opt. with unit
            elif to_parse.match('[\-\+]?[0-9]+(\.[0-9]+)?([Ee][\-\+][0-9]+)?(\s*(%|px|m|u))?'):
                current_result.append('v:' + to_parse.match_group(0))
                mode = 20

            # an identifier
            elif to_parse.match('[a-zA-Z_:][a-zA-Z_:0-9]*'):
                current = to_parse.match_group(0)
                mode = 10

            # opening bracket
            elif to_parse.match('\('):
                result = parse_eval(to_parse, rek=rek+1)
                current_result.append(result)
                mode = 1

            # closing bracket, ',' or ';'
            elif to_parse.match('(\)|,|;)', wind=None):
                return to_parse

            # quoted string
            elif to_parse.match('["\']', wind=None):
                r = parse_string(to_parse)
                current_result.append('v:' + r)
                mode = 20

        elif mode == 1:
            # whitespace
            if to_parse.match('\s+'):
                pass

            elif to_parse.match('\)'):
                mode = 20

        # read an identifier, this could be a function call
        elif mode == 10:
            # it is a function call
            if to_parse.match('\('):
                current_result.append('f:' + current)

                if to_parse.match('\s*\)'):
                    mode = 20

                else:
                    result = parse_eval(to_parse, rek=rek+1)
                    current_result.append(result)
                    mode = 11

            else:
                current_result.append('v:' + current)
                mode = 20

        # inbetween a function call
        elif mode == 11:
            if to_parse.match('\s*[,;]'):
                result = parse_eval(to_parse, rek=rek+1)
                current_result.append(result)

            elif to_parse.match('\s*\)'):
                mode = 20

        # now we are awaiting an operator - or return
        elif mode == 20:
            if to_parse.match('\s+'):
                pass

            elif to_parse.match('^(\)|,|;)', wind=None) or to_parse.to_parse() == '':
                if len(current_result) == 1:
                    return current_result[0]
                else:
                    return current_result

            elif to_parse.match(eval_op_regexp, wind=None):
                current = to_parse.match_group(1)

                j = int(eval_operators[current]['math_level'])

                if j > math_level:
                    to_parse.wind(len(to_parse.match_group(0)))

                    current_op = current
                    math_level = j

                    if len(current_result) == 1:
                        current_result = [ 'o:' + current_op, current_result[0] ]
                    else:
                        current_result = [ 'o:' + current_op, current_result ]

                    result = parse_eval(to_parse, math_level, current_op, rek=rek+1)
                    current_result.append(result)
                    mode = 21

                else:
                    if len(current_result) == 1:
                      return current_result[0]
                    else:
                      return current_result

        elif mode == 21:
            if to_parse.match('\s+'):
                pass

            elif to_parse.match('(\)|,|;)', wind=None) or to_parse.to_parse() == '':
              if len(current_result) == 1:
                  return current_result[0]
              else:
                  return current_result

            elif to_parse.match(eval_op_regexp, wind=None):
                current = to_parse.match_group(1)

                if current == current_op:
                      to_parse.wind(len(to_parse.match_group(0)))

                      parse_eval(to_parse, math_level, current_op, rek=rek+1)
                      current_result.append(result)

                else:
                  j = int(eval_operators[current]['math_level'])

                  if j >= math_level or rek == 0:
                      to_parse.wind(len(to_parse.match_group(0)))

                      current_op = current
                      math_level = j

                      if len(current_result) == 1:
                        current_result = [ 'o:' + current_op, current_result[0] ]
                      else:
                        current_result = [ 'o:' + current_op, current_result ]

                      result = parse_eval(to_parse, math_level, current_op, rek=rek+1)
                      current_result.append(result)

                  else:
                      if len(current_result) == 1:
                        return current_result[0]
                      else:
                        return current_result
