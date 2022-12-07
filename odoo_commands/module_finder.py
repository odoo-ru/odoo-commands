import sys
from collections import namedtuple
from importlib.machinery import FileFinder

import mock
from importlib._bootstrap import ModuleSpec

from importlib._bootstrap_external import _NamespacePath, PathFinder
from importlib.abc import MetaPathFinder


class TracerFinder(MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        print(f'Looking for {fullname=} {path=}')
        return None

odoo_path = '/home/voronin/.local/share/virtualenvs/ruchet-SAKa37C1/lib/python3.6/site-packages/odoo'
odoo_addons_path = '/home/voronin/.local/share/virtualenvs/ruchet-SAKa37C1/lib/python3.6/site-packages/odoo/addons'
odoo_path_base = '/home/voronin/.local/share/virtualenvs/ruchet-SAKa37C1/lib/python3.6/site-packages'
odoo_mock = '/home/voronin/projects/odoo-commands/odoo_commands/odoo'
odoo_mock_base = '/home/voronin/projects/odoo-commands/odoo_commands'

class MockFileFinder(FileFinder):
    # @classmethod
    def find_spec(cls, fullname, target=None):
        print(f'Looking for {fullname=} {target=}')
        if fullname == 'odoo':
            spec = FileFinder.find_spec(fullname, target)
            print(spec)
            return spec
        spec = FileFinder.find_spec(fullname, target)
        print(spec)
        return spec

class MockPathFinder(PathFinder):
    @classmethod
    def find_spec(cls, fullname, path, target=None):
        # fullname_parts = fullname.split('.')
        print(f'Looking for {fullname=} {path=} {target=}')
        if fullname in {'odoo', 'dateutil', 'werkzeug'}:
            spec = PathFinder.find_spec(fullname, [odoo_mock_base], target)
            print(spec)
            return spec
        elif fullname == 'odoo.addons':
            spec = PathFinder.find_spec(fullname, [odoo_mock_base + '/addons'], target)
            print(spec)
            return spec
        # elif fullname == 'odoo.addons.sale':
        elif fullname.startswith('odoo.addons.'):
            spec = PathFinder.find_spec(fullname, [odoo_addons_path], target)
            print(spec)
            return spec
        spec = PathFinder.find_spec(fullname, path, target)
        print(spec)
        return spec

    @classmethod
    def find_spec_OFF(cls, fullname, path, target=None):
        print(f'Looking for {fullname=} {path=}')

        if path is None:
            path = sys.path
        spec = cls._get_spec(fullname, path, target)
        if spec is None:
            return None
        elif spec.loader is None:
            namespace_path = spec.submodule_search_locations
            if namespace_path:
                # We found at least one namespace path.  Return a spec which
                # can create the namespace package.
                spec.origin = None
                spec.submodule_search_locations = _NamespacePath(fullname, namespace_path, cls._get_spec)
                return spec
            else:
                return None
        else:
            return spec


barcode = namedtuple('Module', 'createBarcodeDrawing')
pypdf2 = namedtuple('Module', ['PdfFileWriter', 'PdfFileReader'])
with mock.patch.dict(sys.modules, {
        'reportlab.graphics.barcode': barcode(None),
        'PyPDF2': pypdf2(None, None),
        }):
    sys.meta_path.insert(0, MockPathFinder)
    # sys.meta_path.insert(0, MockFileFinder())
    # import datetime
    # from odoo import models
    from odoo.addons import sale

# class MyLoader(SourceLoader):
#     def __init__(self, fullname, path):
#         self.fullname = fullname
#         self.path = path
#
#     def get_filename(self, fullname):
#         print('get_filename', fullname)
#         return self.path
#
#     def get_data(self, filename):
#         print('get_date', filename)
#         """exec_module is already defined for us, we just have to provide a way
#         of getting the source code of the module"""
#         with open(filename) as f:
#             data = f.read()
#         # do something with data ...
#         # eg. ignore it... return "print('hello world')"
#         return data
#
#
# def hooker(string):
#     return MyLoader
#
# sys.path_hooks.insert(0, FileFinder.path_hook((MyLoader, ['*.py'])))
# sys.path_hooks.insert(0, hooker)
# sys.path_importer_cache.clear()
# invalidate_caches()
