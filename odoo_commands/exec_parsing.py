import pathlib

import pylint
import astroid
from astroid import nodes
from ipdb import iex

from odoo_commands.odoo_mock import models

mock_import = 'from odoo_commands.odoo_mock import '

ODOO_MOCKED_NAMES = {
    'models',
    'fields',
    'api',
    '_',
    # 'SUPERUSER_ID',
}

def replace_import_from(node):
    if node.modname == 'odoo' or node.modname == 'openerp':
        mocked_names = [name[0] for name in node.names if name[0] in ODOO_MOCKED_NAMES]
        if mocked_names:
            return astroid.extract_node(mock_import + ', '.join(mocked_names))
        else:
            return astroid.extract_node(f'_COMMENT = "{node.as_string()}"')

    modname_parts = node.modname.split('.')
    if modname_parts[0] == 'odoo' and modname_parts[1] in {'tools', 'exceptions', 'http', 'addons', 'modules', 'fields'}:
        # return astroid.extract_node('# ' + node.as_string())
        return astroid.extract_node('_odoo_import_turned_to = 0')
    elif modname_parts[0] in {'dateutil', 'werkzeug'}:
        return astroid.extract_node(f'_COMMENT = "{node.as_string()}"')
    return node

def replace_import(node):
    new_names = []
    for name, alias in node.names:
        name_parts = name.split('.')
        if name_parts[0] in {'werkzeug', 'odoo'}:
            pass
        else:
            new_names.append((name, alias))
    if new_names:
        node.names = new_names
        return node
    else:
        return astroid.extract_node(f'_COMMENT = "{node.as_string()}"')

astroid.MANAGER.register_transform(nodes.ImportFrom, replace_import_from)
astroid.MANAGER.register_transform(nodes.Import, replace_import)


# @iex
def parse_module_file_via_exec(path):
    with open(path) as python_file:
        python_module = astroid.parse(python_file.read(), path=path)
        # return python_module
        scope = {'__name__': 'odoo.addons.' + path.stem}
        source = python_module.as_string()
        exec(source, scope)
        return scope
        # print(python_module.as_string())
        # for value in scope.values():
        #     if isinstance(value, models.Model):
        #         yield value
            # raise ZeroDivisionError



path = '/home/voronin/.local/share/virtualenvs/ruchet-SAKa37C1/lib/python3.6/site-packages/odoo/addons/'
module_path = pathlib.Path(path + 'base/res/res_country.py')
# module_path = 'tests/addons/module_name/models/model_name.py'
# m = parse_module_file_via_exec(module_path)
