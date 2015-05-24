class fake_plpy:
    def __init__(self, args=None):
        self.conn = postgresql.open(
            host=(args.host if args and args.host else '{host}'),
            password=(args.password if args and args.password else '{password}'),
            database=(args.database if args and args.database else '{database}'),
            user=(args.user if args and args.user else '{user}')
        )
        self.conn.settings.update({{
# START db.search_path
            'search_path': "{config|db|search_path}"
# END db.search_path
        }})
# START debug.explain_queries
        self.explain_queries = {{ }}
# END debug.explain_queries

    def notice(self, *arg):
        sys.stderr.write('NOTICE: ' + '\n  '.join([str(a) for a in arg]) + '\n')

    def warning(self, *arg):
        sys.stderr.write('WARNING: ' + '\n  '.join([str(a) for a in arg]) + '\n')

    def prepare(self, query, param_type):
        for (i, t) in enumerate(param_type):
            i1 = i + 1
            if t == 'geometry':
                t = 'text::geometry'
            elif t == 'geometry[]':
                t = 'text[]::geometry[]'
            query = query.replace('$' + str(i1), '$' + str(i1) + '::' + t)

        plan = self.conn.prepare(query)
        plan.query = query

        return plan

# START debug.explain_queries
    def record_explain_queries(self, plan, param):
        if not plan.query in self.explain_queries:
            self.explain_queries[plan.query] = {{ 'count': 0 }}
            explain = self.conn.prepare('explain ' + plan.query)
            sys.stderr.write(plan.query)
            self.explain_queries[plan.query]['explain'] = explain(*param)

        self.explain_queries[plan.query]['count'] += 1
# END debug.explain_queries

    def execute(self, plan, param=[]):
# START debug.explain_queries
        self.record_explain_queries(plan, param)
# END debug.explain_queries
        ret = []
        for r in plan(*param):
            if type(r) != postgresql.types.Row:
                return r

            ret.append(dict(r))

        return ret

    def cursor(self, plan, param=[]):
# START debug.explain_queries
        self.record_explain_queries(plan, param)
# END debug.explain_queries
        for r in plan(*param):
            yield dict(r)
