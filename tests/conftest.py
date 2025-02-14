import pathlib
from odoo_commands.project import OdooModule

import pytest


@pytest.fixture(scope='session')
def project_path():
    return pathlib.Path(__file__).parent / 'project'

@pytest.fixture()
def module_a(project_path):
    return OdooModule(project_path / 'addons/module_a')

@pytest.fixture()
def module_name(project_path):
    return OdooModule(project_path / 'addons/module_name')
