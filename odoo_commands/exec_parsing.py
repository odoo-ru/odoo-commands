import pathlib

import pylint
import astroid
from astroid import nodes
from ipdb import iex


mock_import = 'from odoo_commands.odoo_mock import '

ODOO_MOCKED_NAMES = {
    'models',
    'fields',
}

def replace_odoo_imports(node):
    node_type = type(node)
    if node_type is nodes.ImportFrom:
        if node.modname == 'odoo':
            mocked_names = [name[0] for name in node.names if name[0] in ODOO_MOCKED_NAMES]
            # for name, alias in node.names:
            #     if name == 'models':
            return astroid.extract_node(mock_import + ', '.join(mocked_names))
    return node


astroid.MANAGER.register_transform(nodes.ImportFrom, replace_odoo_imports)


@iex
def parse_module_file_via_exec(path):
    with open(path) as python_file:
        python_module = astroid.parse(python_file.read(), path=path)
        scope = {}
        exec(python_module.as_string(), scope)
        return scope
        # print(python_module.as_string())
        # for node in python_module.body:
        #     raise ZeroDivisionError



path = '/home/voronin/.local/share/virtualenvs/ruchet-SAKa37C1/lib/python3.6/site-packages/odoo/addons/'
module_path = pathlib.Path(path + 'base/res/res_country.py')
# module_path = 'tests/addons/module_name/models/model_name.py'
# m = parse_module_file_via_exec(module_path)
