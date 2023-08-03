import pathlib

import pytest


@pytest.fixture(scope='session')
def project_path():
    return pathlib.Path(__file__).parent / 'project'
