#!/usr/bin/python3

import postgresql
import sys

class fake_plpy:
    def __init__(self, args=None):
        self.conn = postgresql.open(
            host=(args.host if args and args.host else '{host}'),
            password=(args.password if args and args.password else '{password}'),
            database=(args.database if args and args.database else '{database}'),
            user=(args.user if args and args.user else '{user}'),
        )
# START explain_queries
        self.explain_queries = {{ }}
# END explain_queries

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

        plan = self.conn.prepare(query)
        plan.query = query

        return plan

    def execute(self, plan, param=[]):
# START explain_queries
        if not plan.query in self.explain_queries:
            self.explain_queries[plan.query] = {{ 'count': 0 }}
            explain = self.conn.prepare('explain ' + plan.query)
            sys.stderr.write(plan.query)
            self.explain_queries[plan.query]['explain'] = explain(*param)

        self.explain_queries[plan.query]['count'] += 1
# END explain_queries
        return [
            dict(r)
            for r in plan(*param)
        ]

    def cursor(self, plan, param=[]):
# START explain_queries
        if not plan.query in self.explain_queries:
            self.explain_queries[plan.query] = {{ 'count': 0 }}
            explain = self.conn.prepare('explain ' + plan.query)
            sys.stderr.write(plan.query)
            self.explain_queries[plan.query]['explain'] = explain(*param)

        self.explain_queries[plan.query]['count'] += 1
# END explain_queries
        for r in plan(*param):
            yield dict(r)

def pgmapcss_{style_id}(bbox=None, scale_denominator=2000, parameters={{}}, _all_style_elements={all_style_elements}):
    import pghstore
    plpy = fake_plpy()
