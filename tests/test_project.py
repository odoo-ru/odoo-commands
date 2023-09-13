import pathlib

from odoo_commands.project import OdooProject


def test_module_graph(project_path):
    project = OdooProject(project_path)
    # assert project.config.project_module_dirs == ['addons']

    assert set(project.expand_deps(project.required_modules).names()) == {
        'module_name',

        'account',
        'analytic',
        'base',
        'product',
        'portal',
        'base_setup',
        'mail',
        'http_routing',
        'decimal_precision',
        'web',
        'bus',
        'web_tour',
        'sale',
        'sales_team',
        'web_planner',
    }

    # sale_module = project.module('sale')
    # assert set(sale_module.expanded_dependencies) == {
    #     'base',
    #     'account',
    #     'analytic',
    #     'product',
    #     'portal',
    #     'base_setup',
    #     'mail',
    #     'http_routing',
    #     'decimal_precision',
    #     'web',
    #     'bus',
    #     'web_tour',
    #     'sales_team',
    #     'web_planner',
    # }
