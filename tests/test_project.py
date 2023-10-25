import pathlib

from odoo_commands.project import OdooProject


def test_module_graph(project_path):
    project = OdooProject(project_path)
    # assert project.config.module_dirs == ['addons']

    required_modules = project.required_modules
    # assert required_modules.names() == {'module_name', 'module_a', 'module_b'}
    # assert required_modules.names() == {'module_name'}
    # assert required_modules.names() == {'base', 'mail'}
    assert required_modules.names() == {'base'}

    assert project.installed_modules.names() == {
        'base',
        'base_import',
        'auth_crypt',
        'iap',
        'web',
        'web_settings_dashboard',
        'web_tour',
        'web_planner',
        'web_editor',
        'web_diagram',
        'web_kanban_gauge',
    }
    # assert set(project.installed_modules.names()) == {
    #     'module_name',
    #
    #     'account',
    #     'analytic',
    #     'base',
    #     'product',
    #     'portal',
    #     'base_setup',
    #     'mail',
    #     'http_routing',
    #     'decimal_precision',
    #     'web',
    #     'bus',
    #     'web_tour',
    #     'sale',
    #     'sales_team',
    #     'web_planner',
    # }

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
