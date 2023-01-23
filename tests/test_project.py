

from odoo_commands.project import OdooProject


def test_module_graph():
    # return
    project = OdooProject(['addons'])
    sale_module = project.module('sale')
    assert set(sale_module.expanded_dependencies) == {
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
    }
