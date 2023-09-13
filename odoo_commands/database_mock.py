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

    def __init__(self, installed_modules):
        self.installed_modules = installed_modules

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
            return [(module.name,) for module in self.installed_modules]

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

        # modules/loading.py:reset_modules_state
        if query in {
            "UPDATE ir_module_module SET state='installed' WHERE state IN ('to remove', 'to upgrade')",
            "UPDATE ir_module_module SET state='uninstalled' WHERE state='to install'",
        }:
            return []

        # ResLang._check_active
        if query == 'SELECT count(1) FROM "res_lang" WHERE ("res_lang"."active" = %s)':
            return [1]

        raise NotImplementedError(f'Unknown SQL query:\n{query}\n\nparams: {params}')

    @property
    @lru_cache(maxsize=1)
    def modules(self):
        return [
            {
                'id': 1,
                'name': module.name,
                'state': 'installed',
                'dbdemo': False,
                'installed_version': '11.0.1.3',
            }
            for module_id, module in enumerate(self.installed_modules, start=1)
        ]

    def decimal_precision(self, names):
        return [(2,)] * len(names)


class CursorMock:
    db = NotImplemented

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
