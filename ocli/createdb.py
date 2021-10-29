import ast
import os

from click_odoo_contrib._addon_hash import addon_hash

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
