import importlib
import logging
import pathlib
import time

logger = logging.getLogger(__name__)

from odoo.modules import initialize_sys_path
initialize_sys_path()

# import odoo.tools.misc
# import odoo.addons.base
# from dateutil.relativedelta import relativedelta


def parse_odoo_module_Import(module_path):
    module_name = module_path.name
    if module_name in {
            # 'base',
            'hw_posbox_upgrade',
            # 'l10n_be_intrastat',
            # 'auth_signup',
            # 'l10n_co',
            # 'iap',
            # 'hw_screen',
            # 'gamification',
            # 'hw_escpos',
        }:
        return []
    t1 = time.time()
    module = importlib.import_module('odoo.addons.' + module_path.name)
    t2 = time.time()
    print(module_name, f'\t\t{t2 - t1:.3f}')
    # if hasattr(module, 'models'):
    return []

    for path in module_path.glob('**/*.py'):
        logger.debug('Parse Odoo module file: %s', path)
        rel_path = path.relative_to(module_path)
        if rel_path.parts[0] in {'controllers', 'tests'}:
            continue
        if path.name.startswith('test_'):
            continue
        if path.name in {'__init__.py', '__manifest__.py'}:
            continue

        # yield from parse_python_module(path)
        # yield from parse_module_file_via_exec(path)


def is_odoo_module(path):
    if isinstance(path, str):
        path = pathlib.Path(path)
    return path.is_dir() and (path / '__manifest__.py').is_file()

def generate(modules_path):
    model_defs = []
    logger.debug('Scan Odoo addons dir: %s', modules_path)
    for path in pathlib.Path(modules_path).iterdir():
        if is_odoo_module(path) and not path.name.startswith('test_'):
            logger.debug('Found Odoo module: %s', path)
            # logger.warning('Found Odoo module: %s', path)
            # model_defs += list(parse_odoo_module(path))
            model_defs += list(parse_odoo_module_Import(path))
            # return parse_module(path)
            # for model_def in parse_module(path):
            #     pass
    return model_defs


path = '/home/voronin/.cache/pypoetry/virtualenvs/odoo-commands-pZzlzv48-py3.6/lib/python3.6/site-packages/odoo/addons'
m = generate(path)

# path = '/home/voronin/.local/share/virtualenvs/ruchet-SAKa37C1/lib/python3.6/site-packages/odoo/addons/l10n_be_intrastat/wizard/xml_decl.py'
# m = generate(pathlib.Path(path))
# m = parse_module_file_via_exec(pathlib.Path(path))
