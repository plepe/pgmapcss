import re
import os
import pgmapcss.mapnik

class ParseFile():
    def __init__(self, filename):
        self._filename = filename

        if os.path.exists(filename):
            self._content = open(filename).read()
        else:
            self._content = pgmapcss.mapnik.get_base_style(filename)

        self._original_content = self._content
        self._to_parse = self._content

    def to_parse(self):
        return self._to_parse

    def set_to_parse(self, s):
        self._to_parse = s

    def content(self):
        return self._content

    def set_content(self, s):
        self._content = s
        self._to_parse = s

    def wind(self, s):
        t = None

        if type(s) == str:
            t = self._to_parse[0:len(s)]
            self._to_parse = self._to_parse[len(s):]

        else:
            t = self._to_parse[0:s]
            self._to_parse = self._to_parse[s:]

        return t

    def rewind(self, s):
        if type(s) == str:
            self._to_parse = s + self._to_parse

        else:
            l = self.pos()
            self._to_parse = self._content[l - s:l] + self._to_parse

    def insert(self, s):
        self._content = self._content[:-len(self._to_parse)] + s + self._content[-len(self._to_parse):]
        self._to_parse = s + self._to_parse

    def match(self, regexp, wind=0):
        self.last_match = re.match(regexp, self._to_parse)

        if self.last_match and wind != None:
            self.wind(self.last_match.group(wind))

        return self.last_match

    def match_groups(self):
        return self.last_match.groups()

    def match_group(self, n):
        return self.last_match.group(n)

    def pos(self):
        return len(self._content) - len(self._to_parse)

    def coord(self):
        parsed = self._content[:-len(self._to_parse)]
        lines = parsed.count('\n')
        last_line_pos = parsed.rfind('\n')

        return [ lines, len(parsed) - last_line_pos - 1 ]

    def show_pos(self, marker_message='here', message='Error parsing'):
        c = self.coord()
        ret = ''

        parsed = self._original_content[:-len(self._to_parse)]
        last_line_pos = parsed.rfind('\n')
        if last_line_pos == -1:
            last_line_pos = 0

        ret += message + '; file: "' + self._filename + '" at line: ' + str( c[0] + 1 ) + ' column: ' + str( c[1] + 1 ) + '\n'
        ret += parsed[last_line_pos:] + self._to_parse[:self._to_parse.find('\n')] + '\n'
        ret += ' ' * (len(parsed) - last_line_pos) + '^-- ' + marker_message

        return ret
