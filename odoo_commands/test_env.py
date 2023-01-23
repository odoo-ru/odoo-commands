import odoo
from odoo.api import Environments


# from IPython import start_ipython


def get_env():
    # config.parse_config([])
    odoo.tools.config.parse_config(['-d', 'prod2'])
    # config.parse_config(['--workers', '1'])
    odoo.cli.server.report_configuration()
    odoo.service.server.start(preload=[], stop=True)

    # with odoo.api.Environment.manage():
    odoo.api.Environment._local.environments = Environments()
    registry = odoo.registry('prod2')
    # with registry.cursor() as cr:
    cr = registry.cursor()
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    # env.reset()
    # start_ipython(argv=[], user_ns={'env': env})

    print(env['res.lang'].search([]))
    # yield env
    return env


# env = next(get_env())
env = get_env()
# cr.close()
# odoo.api.Environment._local.__release_local__()
