from .default import default
from ..compiler.compile_eval import compile_eval
import re

class dashes(default):
    def compile_check(self, value):
        return 'eval_to_dashes([' + value + '], current)'

    def __parse(self, param):
        if param == 'none':
            return param

        ret = param
        ret = str.replace(ret, ';', ',')
        ret = str.replace(ret, ' ', '')

        if len([
            t
            for t in ret.split(',')
            if not re.match('[0-9]+$', t)
        ]):
            print("invalid dashes value '{}'".format(param))
            return 'none'

        return ret

    def compile(self, prop):
        return repr(self.__parse(prop['value']))

    def stat_value(self, prop):
        return self.__parse(prop['value'])
