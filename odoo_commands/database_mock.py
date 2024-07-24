from odoo_commands.project import Module, ModuleSet
from functools import lru_cache


class FakeDatabase:
    table_existing_query = """
        SELECT c.relname
          FROM pg_class c
          JOIN pg_namespace n ON (n.oid = c.relnamespace)
         WHERE c.relname IN %s
           AND c.relkind IN ('r', 'v', 'm')
           AND n.nspname = current_schema
    """

    "id", "name", "category_id", "shortdesc", "summary", "description", "author", "maintainer", "contributors",
    "website", "latest_version", "published_version", "url", "sequence", "auto_install", "state", "demo",
    "license", "menus_by_module", "reports_by_module", "views_by_module", "application", "icon", "to_buy",

    "create_uid" as "create_uid", "ir_module_module".
    "create_date" as "create_date", "ir_module_module".
    "write_uid" as "write_uid", "ir_module_module".
    "write_date" as "write_date"

    def __init__(self, installed_modules: ModuleSet):
        self.data = {}
        self.installed_modules = installed_modules

    @staticmethod
    def _module_vals(module: Module):
        return {
            'name': module.name,
            'category_id': None,
            'shortdesc': module.shortdesc,
            'summary': module.summary,
            'description': module.description,
            'author': module.author,
            'maintainer': module.maintainer,
            'contributors': module.contributors,
        }

    def fill_module_table(self, installed_modules: ModuleSet):
        # module_dict = self.data.setdefault('ir_module_module', [])
        module_data = []
        for record_id, module in enumerate(installed_modules, start=1):
            module_vals = self._module_vals(module)
            module_vals.update({
                'id': record_id,
            })
            module_data.append(module_vals)

        self.data['ir_module_module'] = module_data


    def execute(self, query, params):
        print(f'{query!r}')
        print(f'{params!r}')

        if query in {
            # self.table_existing_query,
            "SELECT proname FROM pg_proc WHERE proname='unaccent'",
            "SELECT * FROM ir_model_fields WHERE state='manual'",
            # Odoo 15
            "SELECT proname FROM pg_proc WHERE proname='word_similarity'",
            "SET SESSION lock_timeout = '15s'",
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

        # Odoo 15
        if query == 'SELECT "ir_module_module".id FROM "ir_module_module" WHERE ("ir_module_module"."state" = %s) ORDER BY  "ir_module_module"."name"  ':
            if params == ['installed']:
                # return [(module.name,) for module in self.installed_modules]
                return [(1,), (2,)]

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


# class CursorMockMeta(type):
#     def __instancecheck__(self, other):
#         print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
#         print(other)
#         return True


from odoo.sql_db import BaseCursor

class CursorMock(BaseCursor):
    db = NotImplemented

    def __init__(self, pool, dbname, dsn, serialized=True):
        self.dbname = dbname
        self.sql_log_count = 0
        self.transaction = None

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

    def close(self):
        pass

    def split_for_in_conditions(self, ids, size=None):
        return ids


def cursor_mock_class(installed_module_names_callback):

    class CursorDbMock(CursorMock):
        db = FakeDatabase(installed_module_names_callback)

    return CursorDbMock
