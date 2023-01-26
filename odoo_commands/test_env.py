import contextlib
import time
from functools import lru_cache

import mock
from odoo.modules.registry import Registry

from odoo_commands.database_mock import cursor_mock_class

# from functools import cached_property

s1 = time.time()

import odoo
from odoo.api import Environments

s2 = time.time()
print('S >>', format(s2 - s1, '.3f'))



# from IPython import start_ipython

cr = None

def get_env():
    global cr

    # config.parse_config([])
    odoo.tools.config.parse_config(['-d', 'test-oc'])
    # config.parse_config(['--workers', '1'])
    odoo.cli.server.report_configuration()
    odoo.service.server.start(preload=[], stop=True)

    # with odoo.api.Environment.manage():
    t0 = time.time()
    odoo.api.Environment._local.environments = Environments()
    t1 = time.time()
    print('0 >>>', format(t1 - t0, '.3f'))
    registry = odoo.registry('test-oc')
    t2 = time.time()
    print('1 >>>', format(t2 - t1, '.3f'))
    # with registry.cursor() as cr:
    cr = registry.cursor()
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    t3 = time.time()
    print('2 >>>', format(t3 - t2, '.3f'))
    # env.reset()
    # start_ipython(argv=[], user_ns={'env': env})

    print(env['res.lang'].search([]))
    # yield env
    return env


class Klass:
    def __init__(self):
        self._env = None

    # @property
    # def env(self):
    #     if not self._env:
    #         self._env = next(self.env_init)
    #
    #     return self._env

    @property
    def env_OFF(self):
        if not getattr(self, '_env', None):
            t0 = time.time()
            # odoo.api.Environment._local.environments = Environments()
            self._env_manager = odoo.api.Environment.manage()
            self._env_manager.__enter__()
            t1 = time.time()
            print('0 >>>', format(t1 - t0, '.3f'))
            registry = odoo.registry('test-oc')
            t2 = time.time()
            print('1 >>>', format(t2 - t1, '.3f'))
            # with registry.cursor() as cr:
            cr = registry.cursor()
            self._env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
            t3 = time.time()
            print('2 >>>', format(t3 - t2, '.3f'))

        return self._env

    @contextlib.contextmanager
    def init_env(self, database):

        was_env_used = False

        def env_generator():
            nonlocal was_env_used
            with odoo.api.Environment.manage():
                print('registry')
                with odoo.registry(database).cursor() as cr:
                    was_env_used = True
                    yield odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})

        env_gen = env_generator()

        # @cached_property
        @property
        def env_property(self):
            return next(env_gen)

        # self.env_init = lazy_env(db)
        # yield env_property
        # TODO Use functools.cached_property for Python3.8+
        yield property(lru_cache(maxsize=1)(lambda self: next(env_gen)))
        # yield property(lru_cache(maxsize=1)(env_gen.__next__))

        if was_env_used:
            # exit odoo context managers
            next(env_gen)
        # self.env_init = None
        # self._env = None

    def payload(self):
        Registry.in_test_mode = lambda self: True

        with mock.patch('odoo.sql_db.Cursor', cursor_mock_class(lambda self: ['base'])):
            with self.init_env('test-oc') as type(self).env:
                # print(self.env['res.lang'].search([]))
                pass

# env = next(get_env())
# env = get_env()
# cr.close()
# odoo.api.Environment._local.__release_local__()

obj = Klass()
obj.payload()
