import mock
import odoo
from odoo.modules.registry import Registry
from odoo.sql_db import Cursor, ConnectionPool


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


# class CursorMock(Cursor):
class CursorMock:
    # def __init__OFF(self, pool, dbname, dsn, serialized=True):
    def __init__(self, pool, dbname, dsn, serialized=True):
        self.dbname = dbname
        return
        # self.sql_from_log = {}
        # self.sql_into_log = {}

        # default log level determined at cursor creation, could be
        # overridden later for debugging purposes
        # self.sql_log = _logger.isEnabledFor(logging.DEBUG)

        # self.sql_log_count = 0

        # avoid the call of close() (by __del__) if an exception
        # is raised by any of the following initialisations
        # self._closed = True

        self.__pool = pool
        self.dbname = dbname
        # Whether to enable snapshot isolation level for this cursor.
        # see also the docstring of Cursor.
        self._serialized = serialized

        self._cnx = pool.borrow(dsn)
        self._obj = self._cnx.cursor()
        if self.sql_log:
            self.__caller = frame_codeinfo(currentframe(), 2)
        else:
            self.__caller = False
        self._closed = False  # real initialisation value
        self.autocommit(False)
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
                return [('base',)]

        raise ValueError(f'Unknown query: {self.query}: {self.params}')

    def dictfetchall(self):
        if self.query == "SELECT name, id, state, demo AS dbdemo, latest_version AS installed_version  FROM ir_module_module WHERE name IN %s":
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


def db_connect(to, allow_uri=False):
    return ConnectionMock(PoolMock(), to, {})

    global _Pool
    if _Pool is None:
        _Pool = ConnectionPool(int(tools.config['db_maxconn']))

    db, info = connection_info_for(to)
    if not allow_uri and db != to:
        raise ValueError('URI connections not allowed')
    return Connection(_Pool, db, info)


def is_initialized(cr):
    return True

def reset_modules_state(dbname):
    print('reset_modules_state')

Registry.setup_signaling = lambda self: None
import odoo.modules
odoo.modules.reset_modules_state = lambda dbname: None


def get_env():
    # with mock.patch('odoo.sql_db.db_connect', db_connect):
    with mock.patch('odoo.sql_db.Cursor', CursorMock), \
        mock.patch('odoo.sql_db.ConnectionPool', ConnectionPoolMock), \
        mock.patch('odoo.modules.db.is_initialized', is_initialized), \
        mock.patch('odoo.modules.registry.Registry', MockRegistry), \
        mock.patch('odoo.modules.loading.reset_modules_state', reset_modules_state):

        # registry = odoo.registry('none')
        registry = Registry('none')
        cr = registry.cursor()
        # env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
        # registry = MockRegistry('none')

        with odoo.api.Environment.manage(), odoo.registry('none').cursor() as cr:
            env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
            env.reset()
            yield env

        # with registry.cursor() as cr:
        #     env = odoo.api.Environment(cr, 1, {})

        # with odoo.api.Environment.manage():
            # registry = odoo.registry('none')
            # registry = MockRegistry('none')

env = next(get_env())
