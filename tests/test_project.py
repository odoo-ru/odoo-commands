from pathlib import Path

from odoo_commands.project import OdooProject, OdooModule, ModuleSet


class TestModule:
    def test_module(self, project_path):
        module_a = OdooModule(project_path / 'addons/module_a')
        module_a2 = OdooModule(project_path / 'addons/module_a')
        assert module_a == module_a2
        assert module_a is module_a2

    def test_relative_path(self, module_a):
        assert module_a / 'models/model.py' == Path(module_a.path, 'models/model.py')


def test_topologic_dependencies(project_path):
    project = OdooProject(project_path)
    # assert project.config.module_dirs == ['addons']

    module = project.module('module_a')
    assert module.name == 'module_a'

    module_list = project.topologic_dependencies(project.expand_dependencies(ModuleSet({module})))
    assert [module.name for module in module_list] == [
        'module_c',
        'module_b',
        'module_a',
    ]


def test_module_graph(project_path):
    project = OdooProject(project_path, modules=['module_a'])
    # assert project.config.module_dirs == ['addons']

    required_modules = project.required_modules
    # assert required_modules.names() == {'module_name', 'module_a', 'module_b'}
    # assert required_modules.names() == {'module_name'}
    # assert required_modules.names() == {'base', 'mail'}
    assert required_modules.names() == {'module_a'}

    assert project.installed_modules.names() > {
        'module_a',
        'module_b',
        'module_c',
    }
