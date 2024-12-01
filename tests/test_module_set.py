from odoo_commands.project import OdooModuleSet, OdooProject, OdooModule


def test_operations():
    m = OdooModuleSet({1, 2, 3})
    m2 = OdooModuleSet({2})
    m4 = OdooModuleSet({4})

    assert isinstance(m - m2, OdooModuleSet)
    assert isinstance(m & m2, OdooModuleSet)
    assert isinstance(m | m4, OdooModuleSet)

    assert m - m2 == {1, 3}


def test_module_graph(project_path):
    project = OdooProject(project_path)

    module_a = OdooModule(project_path / 'addons/module_a')
    module_b = OdooModule(project_path / 'addons/module_b')
    modules = OdooModuleSet({module_a, module_b})

    assert modules.names() == {'module_a', 'module_b'}
    assert modules.depends() == {'module_c'}
