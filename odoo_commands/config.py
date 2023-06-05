from collections import OrderedDict
from pathlib import Path
from typing import List

from dataclasses import dataclass, field
import tomlkit


# @dataclass(repr=False, eq=False)
@dataclass(order=True)
class Config:
    project_module_dirs: List[str] = field(default_factory=list)
    third_party_module_dirs: List[str] = field(default_factory=list)


class Config2:

    def __init__(self, values):
        if not values:
            values = {}
        project_module_dirs = ()
        third_party_module_dirs = ()
        self.values = OrderedDict([
            ('project_module_dirs', []),
            ('third_party_module_dirs', []),
        ])

    def __getattr__(self, item):
        return self.values[item]

    def __getitem__(self, item):
        return self.__getattr__(item.replace('-', '_'))

    def __setattr__(self, key, value):
        self.values[key] = value

    def __setitem__(self, key, value):
        self.values[key.replace('-', '_')] = value

    # def _from_dict(self, dictionary):
    #     for


def read_config(path='.'):
    path = Path(path)
    if path.is_dir():
        path /= 'pyproject.toml'

    with open(path) as config_file:
        config = tomlkit.load(config_file)

# def pyproject_odoo(path='.'):
#     config = pyproject(path)
    odoo_config = {}
    if 'tool' in config:
        odoo_config = config['tool'].get('odoo')
        odoo_config = odoo_config.unwrap() if odoo_config else {}

    return Config(**odoo_config)
            # return odoo_config.unwrap()
