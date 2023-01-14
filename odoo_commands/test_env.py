import odoo
from IPython import start_ipython


def get_env():
    # config.parse_config([])
    odoo.tools.config.parse_config(['-d', 'prod2'])
    # config.parse_config(['--workers', '1'])
    odoo.cli.server.report_configuration()
    odoo.service.server.start(preload=[], stop=True)

    with odoo.api.Environment.manage(), odoo.registry('prod2').cursor() as cr:
        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
        # env.reset()
        start_ipython(argv=[], user_ns={'env': env})

        print(env['res.lang'].search([]))
        yield env

env = next(get_env())
