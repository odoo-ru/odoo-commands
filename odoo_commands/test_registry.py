import time
s1 = time.time()

import logging
import mock
# from IPython import start_ipython

import odoo
from odoo.modules.registry import Registry
# from odoo.sql_db import Cursor, ConnectionPool
from odoo.tools import config

s2 = time.time()
print('01 >>', format(s2 - s1, '.2f'))


class MockRegistry(Registry):
    # def init(self, db_name):
    #     super().init(db_name)
    #     self._db = None

    def setup_signaling(self):
        print('setup_signaling')


class PostgresCursorMock:
    pass


class PostgresConnectionMock:
    def cursor(self):
        return PostgresCursorMock()


# class ConnectionPoolMock(ConnectionPool):
class ConnectionPoolMock:
    def __init__(self, maxconn=64):
        self._maxconn = max(maxconn, 1)

    def borrow(self, connection_info):
        return PostgresConnectionMock()


class ConnectionMock:
    pass

_logger = logging.getLogger(__name__)

# class CursorMock(Cursor):
class CursorMock:
#     def __init__OFF(self, pool, dbname, dsn, serialized=True):
    def __init__(self, pool, dbname, dsn, serialized=True):
        self.dbname = dbname
        return
        self.sql_from_log = {}
        self.sql_into_log = {}

        # default log level determined at cursor creation, could be
        # overridden later for debugging purposes
        self.sql_log = _logger.isEnabledFor(logging.DEBUG)

        self.sql_log_count = 0

        # avoid the call of close() (by __del__) if an exception
        # is raised by any of the following initialisations
        self._closed = True

        self.__pool = pool
        self.dbname = dbname
        # Whether to enable snapshot isolation level for this cursor.
        # see also the docstring of Cursor.
        self._serialized = serialized

        # OFFFFFFFFFFFFFFFFF
        self._cnx = pool.borrow(dsn)
        self._obj = self._cnx.cursor()
        # self._cnx = None
        # self._obj = None

        if False:
        # if self.sql_log:
            self.__caller = frame_codeinfo(currentframe(), 2)
        else:
            self.__caller = False
        self._closed = False  # real initialisation value
        # self.autocommit(False)
        self.__closer = False

        self._default_log_exceptions = True

        self.cache = {}

        # event handlers, see method after() below
        self._event_handlers = {'commit': [], 'rollback': []}

    def execute(self, query, params=None, log_exceptions=None):
        print(f'{query}: {params}')
        self.query = query
        self.params = params

    def fetchall(self):
        if self.query == "SELECT proname FROM pg_proc WHERE proname='unaccent'":
            return ([])
        elif self.query == "SELECT name from ir_module_module WHERE state IN %s":
            if self.params == (('installed', 'to upgrade', 'to remove'),):
                # return [('base',)]
                return [(m,) for m in {
                    'base',
                    'account',
                    'analytic',
                    'product',
                    'portal',
                    'base_setup',
                    'mail',
                    'http_routing',
                    'decimal_precision',
                    'web',
                    'bus',
                    'web_tour',
                    'sales_team',
                    'web_planner',
                }]

        raise ValueError(f'Unknown query: {self.query}: {self.params}')

    def dictfetchall(self):
        if self.query == "SELECT name, id, state, demo AS dbdemo, latest_version AS installed_version  FROM ir_module_module WHERE name IN %s":
            result = []
            id_counter = 10
            for module in self.params:
                result.append({
                    'dbdemo': False,
                    'id': 1 if module == 'base' else id_counter,
                    'installed_version': '11.0.1.3',
                    'name': module,
                    'state': 'installed',
                })
                id_counter += 1
            return result

            if self.params == (('base',),):
                return [
                    {
                        'dbdemo': False,
                        'id': 1,
                        'installed_version': '11.0.1.3',
                        'name': 'base',
                        'state': 'installed',
                    },
                ]
        elif self.query == 'SELECT * FROM ir_model WHERE state=%s':
            if self.params == ['manual']:
                return []
        elif self.query == "SELECT * FROM ir_model_fields WHERE state='manual'":
            return []

        raise ValueError('Unknown query')

    def commit(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __del__(self):
        pass

    def close(self):
        pass

    def close_OFF(self):
        return self._close(False)

    def _close_OFF(self, leak=False):
        global sql_counter

        if not self._obj:
            return

        del self.cache

        if self.sql_log:
            self.__closer = frame_codeinfo(currentframe(), 3)

        # simple query count is always computed
        sql_counter += self.sql_log_count

        # advanced stats only if sql_log is enabled
        self.print_log()

        self._obj.close()

        # This force the cursor to be freed, and thus, available again. It is
        # important because otherwise we can overload the server very easily
        # because of a cursor shortage (because cursors are not garbage
        # collected as fast as they should). The problem is probably due in
        # part because browse records keep a reference to the cursor.
        del self._obj
        self._closed = True

        # Clean the underlying connection.
        self._cnx.rollback()

        if leak:
            self._cnx.leaked = True
        else:
            chosen_template = tools.config['db_template']
            templates_list = tuple(set(['template0', 'template1', 'postgres', chosen_template]))
            keep_in_pool = self.dbname not in templates_list
            self.__pool.give_back(self._cnx, keep_in_pool=keep_in_pool)


def is_initialized(cr):
    return True

def reset_modules_state(dbname):
    print('reset_modules_state')

Registry.setup_signaling = lambda self: None
import odoo.modules
odoo.modules.reset_modules_state = lambda dbname: None


def start_env():
    t01 = time.time()
    config.parse_config([])
    # config.parse_config(['-d', 'prod2'])
    # config.parse_config(['--workers', '1'])
    odoo.cli.server.report_configuration()
    odoo.service.server.start(preload=[], stop=True)

    t02 = time.time()
    print('1 >>>', format(t02 - t01, '.2f'))

    # with mock.patch('odoo.sql_db.db_connect', db_connect):
    with mock.patch('odoo.sql_db.Cursor', CursorMock), \
        mock.patch('odoo.modules.db.is_initialized', is_initialized), \
        mock.patch('odoo.modules.loading.reset_modules_state', reset_modules_state):
        t03 = time.time()
        print('2 >>>', format(t03 - t02, '.2f'))

        # registry = odoo.registry('none')
        # registry = Registry('none')
        # cr = registry.cursor()
        # env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
        # registry = MockRegistry('none')

        with odoo.api.Environment.manage(), odoo.registry('none').cursor() as cr:
            env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
            t04 = time.time()
            print('3 >>>', format(t04 - t03, '.2f'))
            print('>>>>>', format(t04 - s1, '.2f'))
            # start_ipython(argv=[], user_ns={'env': env})
            # yield env

        # with registry.cursor() as cr:
        #     env = odoo.api.Environment(cr, 1, {})

        # with odoo.api.Environment.manage():
            # registry = odoo.registry('none')
            # registry = MockRegistry('none')

s10 = time.time()
print('02 >>', format(s10 - s2, '.2f'))

start_env()
