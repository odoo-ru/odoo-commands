from odoo_commands.project import ModuleSet, OdooProject, Module


def test_operations():
    m = ModuleSet({1, 2, 3})
    m2 = ModuleSet({2})
    m4 = ModuleSet({4})

    assert isinstance(m - m2, ModuleSet)
    assert isinstance(m & m2, ModuleSet)
    assert isinstance(m | m4, ModuleSet)

    assert m - m2 == {1, 3}


def test_module_graph(project_path):
    project = OdooProject(project_path)

    module_a = Module(project_path / 'addons/module_a')
    module_b = Module(project_path / 'addons/module_b')
    modules = ModuleSet({module_a, module_b})

    assert modules.names() == {'module_a', 'module_b'}
    assert modules.depends() == {'module_c'}
