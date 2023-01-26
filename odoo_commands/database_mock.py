from functools import lru_cache


class FakeDatabase:
    table_existing_query = """
        SELECT c.relname
          FROM pg_class c
          JOIN pg_namespace n ON (n.oid = c.relnamespace)
         WHERE c.relname IN %s
           AND c.relkind IN ('r', 'v', 'm')
           AND n.nspname = 'public'
    """

    def __init__(self, installed_module_names_callback=NotImplemented):
        if callable(installed_module_names_callback):
            installed_module_names_callback = property(lru_cache(maxsize=1)(installed_module_names_callback))
            type(self).installed_module_names_callback = installed_module_names_callback
        # self.installed_module_names_callback = installed_module_names_callback

    def execute(self, query, params):
        if query in {
            # self.table_existing_query,
            "SELECT proname FROM pg_proc WHERE proname='unaccent'",
            "SELECT * FROM ir_model_fields WHERE state='manual'",
        }:
            return []

        if (query, params) in (
            ('SELECT * FROM ir_model WHERE state=%s', ['manual']),
        ):
            return []

        if query == self.table_existing_query and params == [('ir_module_module',)]:
            return [(1,)]

        if (
            query == "SELECT name from ir_module_module WHERE state IN %s"
            and params == (('installed', 'to upgrade', 'to remove'),)
        ):
            return [(module_name,) for module_name in self.installed_module_names_callback]

        if query == "SELECT name, id, state, demo AS dbdemo, latest_version AS installed_version  FROM ir_module_module WHERE name IN %s":
            result = []
            for module in self.modules:
                if module['name'] in params:
                    module_copy = module.copy()
                    module_copy['dbdemo'] = module_copy.pop('demo')
                    result.append(module_copy)
            return result

        if query == 'select digits from decimal_precision where name=%s':
            return self.decimal_precision(params)

        raise NotImplementedError(f'Unknown SQL query:\n{query}\n\nparams: {params}')

    @property
    @lru_cache(maxsize=1)
    def modules(self):
        return [
            {
                'id': 1,
                'name': module_name,
                'state': 'installed',
                'dbdemo': False,
                'installed_version': '11.0.1.3',
            }
            for module_id, module_name in enumerate(self.installed_module_names_callback, start=1)
        ]

    def decimal_precision(self, names):
        return [(2,)] * len(names)


class CursorMock:
    db = FakeDatabase()

    def __init__(self, pool, dbname, dsn, serialized=True):
        self.dbname = dbname

    def execute(self, query, params=None, log_exceptions=None):
        self.result = self.db.execute(query, params)
        self.result_iter = iter(self.result)

    def fetchone(self):
        return [next(self.result_iter)]

    def fetchall(self):
        return list(self.result_iter)

    # dictfetchone = fetchone
    dictfetchall = fetchall

    def commit(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def close(self):
        pass


def cursor_mock_class(installed_module_names_callback):

    class CursorDbMock(CursorMock):
        db = FakeDatabase(installed_module_names_callback)

    return CursorDbMock
