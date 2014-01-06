class ParseError(Exception):
    def __init__(self, pf, value):
        self.pf = pf
        self.value = value

    def __str__(self):
        return self.pf.show_pos(message=self.value)
