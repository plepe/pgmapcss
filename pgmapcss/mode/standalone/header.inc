#!/usr/bin/python3

import postgresql
import sys

class fake_plpy:
    def __init__(self):
        self.conn = postgresql.open(
            host='{host}',
            password='{password}',
            database='{database}',
            user='{user}'
        )

    def notice(self, *arg):
        sys.stderr.write('NOTICE: ' + ' '.join([repr(a) for a in arg]) + '\n')

    def warning(self, *arg):
        sys.stderr.write('WARNING: ' + ' '.join([repr(a) for a in arg]) + '\n')

    def prepare(self, query, param_type):
        for (i, t) in enumerate(param_type):
            i1 = i + 1
            if t == 'geometry':
                t = 'text'
            elif t == 'geometry[]':
                t = 'text[]'
            query = query.replace('$' + str(i1), '$' + str(i1) + '::' + t)

        return self.conn.prepare(query)

    def execute(self, plan, param=[]):
        return [
            dict(r)
            for r in plan(*param)
        ]

def pgmapcss_{style_id}(bbox=None, scale_denominator=2000, _all_style_elements={all_style_elements}):
    plpy = fake_plpy()
