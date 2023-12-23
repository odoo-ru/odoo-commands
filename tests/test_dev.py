import pathlib

from odoo_commands.project import OdooProject, ModuleSet


def test_module_graph(project_path):
    project = OdooProject(project_path)
    # assert project.config.module_dirs == ['addons']

    module = project.module('module_name')
    assert module.name == 'module_name'

    module_list = project.topologic_dependencies(project.expand_dependencies(ModuleSet({module})))
    assert [module.name for module in module_list] == [
        'base',
        'decimal_precision',
        'web',
        'base_setup',
        'bus',
        'web_tour',
        'mail',
        'analytic',
        'http_routing',
        'portal',
        'product',
        'web_planner',
        'account',
        'sales_team',
        'sale',
        'module_name',
    ]
