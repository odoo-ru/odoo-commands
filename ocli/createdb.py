import ast
import glob
import os
from functools import lru_cache

from click_odoo_contrib._addon_hash import addon_hash


def addons_hash(module_names, with_demo):
    h = hashlib.sha1()
    h.update("!demo={}!".format(int(bool(with_demo))).encode("utf8"))
    for module_name in sorted(expand_dependencies(module_names, True, True)):
        module_path = odoo.modules.get_module_path(module_name)
        h.update(module_name.encode("utf8"))
        for filepath in _walk(module_path):
            h.update(filepath.encode("utf8"))
            with open(os.path.join(module_path, filepath), "rb") as f:
                h.update(f.read())
    return h.hexdigest()


EXCLUDE_PATTERNS = [
    '*.pyc',
    '*.pyo',
    'i18n/*.pot',
    'i18n_extra/*.pot',
    'static/*',
]

keep_languages = ['en', 'ru']

def module_hash(module_path):
    return addon_hash(module_path, EXCLUDE_PATTERNS, keep_languages)


def read_manifest(addon_dir):
    manifest_path = os.path.join(addon_dir, '__manifest__.py')
    # if not os.path.isfile(manifest_path):
    #     raise FileNotFoundError("No Odoo manifest found in %s" % addon_dir)
    with open(manifest_path) as manifest_file:
        return ast.literal_eval(manifest_file.read())

contrib_module_path = '/home/voronin/.local/share/virtualenvs/sintez_addons-7QRHjYmJ/lib/python3.6/site-packages/odoo/addons'

def module_dependencies(module_dir):
    return read_manifest(module_dir).get('depends', [])


def contrib_module_deps(contrib_module_path):
    res = {}
    for module_dir in glob.iglob(contrib_module_path + '/*'):
        if module_dir.endswith('__pycache__') or module_dir.endswith('__init__.py'):
            continue
        res[module_dir] = module_dependencies(module_dir)
    return res


class OdooModules:
    def __init__(self, module_paths, modules_to_install):
        self.module_paths = module_paths

    def module_path(self, module_name):
        for module_path in self.module_paths:
            module_dir =
            if os.path.isdir(os.path.join(module_path, module_name)):


    def module_expanded_deps(self, module_name):
        res = set()
        for dep in self.module_deps(module_name):
            res.add(dep)
            res.update(self.module_expanded_deps(dep))
        return res

    # @lru_cache
    def all_needed_modules(self):


    def modules_cache(self, timestamp):
        # to_install + their deps - their unwanted deps - old modules - their deps


# def module_graph(odoo_version, modules):
#     pass
#
# def modules_cache(module_paths, modules, timestamp):
#     pass


def create_database(name, modules):
    month_cache = modules_cache(modules_paths, modules, timestamp)

