from .default import default

class dashes(default):
    def compile_check(self, value):
        return 'str.replace(str.replace(' + value + ", ';', ','), ' ', '')"

    def __parse(self, ret):
        ret = str.replace(ret, ';', ',')
        ret = str.replace(ret, ' ', '')
        return ret

    def compile(self, prop):
        return repr(self.__parse(prop['value']))

    def stat_value(self, prop):
        return self.__parse(prop['value'])
