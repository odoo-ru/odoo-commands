import ast
import functools
import os
import pathlib
from collections import ChainMap
from pathlib import Path
from functools import lru_cache
from typing import Iterable, Container

import dataclasses
from babel.core import Locale

from odoo_commands.config import read_config, Config


class Module:
    # TODO Add slots
    # __slots__ = ('path', 'name')

    # Default info from odoo/modules/module.py:load_information_from_description_file()
    default_info = {
        'application': False,
        'author': 'Odoo S.A.',
        'auto_install': False,
        'category': 'Uncategorized',
        'depends': [],
        'description': '',
        # 'icon': get_module_icon(module),
        'installable': True,
        'license': 'LGPL-3',
        'post_load': None,
        'version': '1.0',
        'web': False,
        'website': 'https://www.odoo.com',
        'sequence': 100,
        'summary': '',
    }

    _cache = {}

    def __new__(cls, path, *args, **kwargs):
        path = Path(path).resolve()
        if not is_module(path):
            raise ValueError()

        if path in cls._cache:
            return cls._cache[path]

        instance = super().__new__(cls, *args, **kwargs)
        instance.path = path
        instance.name = path.name
        cls._cache[path] = instance
        return instance

    def __repr__(self):
        return f'OdooModule({self.name!r})'

    def __eq__(self, other):
        return self.path == other.path

    def __hash__(self):
        return self.path.__hash__()

    def __truediv__(self, path):
        return self.path / path

    @property
    @lru_cache(maxsize=None)
    def manifest(self):
        with open(self.path / '__manifest__.py') as manifest_file:
            return ast.literal_eval(manifest_file.read())

    def __getattr__(self, item):
        if item in self.manifest:
            return self.manifest[item]
        else:
            return self.default_info[item]

    @property
    @lru_cache(maxsize=1)
    def icon(self):
        if 'icon' in self.manifest:
            return self.manifest['icon']
        # Copy-paste from odoo/modules/module.py:get_module_icon()
        icon_default_path = 'static/description/icon.png'
        if (self.path / icon_default_path).exists():
            return f'/{self.name}/{icon_default_path}'
        return f'/base/{icon_default_path}'

    @lru_cache(maxsize=1)
    def version(self, serie):
        # Copy-paste from odoo/modules/module.py:adapt_version()
        version = self.__getattr__('version')
        if version == serie or not version.startswith(serie + '.'):
            version = '%s.%s' % (serie, version)
        return version

    # TODO Read description from file

    def data_file_path(self):
        yield from self.manifest.get('data', [])

    @property
    def depends(self):
        return self.manifest.get('depends', [])

    def _file_translations(self, po_file_name):
        from odoo.tools.translate import PoFile
        # from odoo.tools.translate import PoFileReader

        result = {}
        for subdir in ['i18n_extra', 'i18n']:
            po_file_path = self / subdir / po_file_name
            if not po_file_path.exists():
                continue
            with open(po_file_path, 'rb') as f:
                for translation in PoFile(f):
                # for translation in PoFileReader(f):
                    # Odoo 11 returns
                    # (trans_type, name, res_id, source, trad, '\n'.join(comments))
                    # print(translation)
                    result[translation[:4]] = translation[4]

        return result

    @lru_cache()
    def translations(self, locale_identifier):
        locale = Locale.parse(locale_identifier)

        base_trans = self._file_translations(f'{locale.language}.po')
        if not locale.territory or locale.territory.lower() == locale.language:
            return base_trans

        # if locale.territory and locale.territory.lower() != locale.language:
        spec_trans = self._file_translations(f'{locale_identifier}.po')
        return ChainMap(spec_trans, base_trans)

# https://stackoverflow.com/questions/798442/what-is-the-correct-or-best-way-to-subclass-the-python-set-class-adding-a-new
def wrap(method):
    @functools.wraps(method)
    def wrapped_method(*args, **kwargs):
        return ModuleSet(method(*args, **kwargs))
    return wrapped_method


class ModuleSet(set):# -> Set[Module]
    def names_list(self):
        return sorted(module.name for module in self)

    def names(self):
        return {module.name for module in self}

    def depends(self):
        return set().union(*[module.depends for module in self]) - self.names()

    def sorted(self):
        return sorted(self, key=lambda m: m.name)

    for method in [
        '__or__',
        '__and__',
        '__sub__',
        'difference',
        'difference_update',
        'intersection_update',
        'symmetric_difference',
        'symmetric_difference_update',
        'intersection',
        'union',
        'copy',
    ]:
        exec(f'{method} = wrap(set.{method})')


def is_module(path: Path):
    return (path / '__manifest__.py').is_file()


class OdooProject:
    def __init__(self, path='.', modules=None, **options):
        self.path = pathlib.Path(path).resolve()
        self.modules = modules

        config_dict = dataclasses.asdict(self.project_file_config)
        config_dict.update(options)
        self.project_config = Config(**config_dict)

    @property
    def project_file_config(self):
        return read_config(self.path / 'pyproject.toml')

    @property
    def project_module_paths(self):
        return [(self.path / path) for path in self.project_config.project_module_dirs]

    @property
    def third_party_module_paths(self):
        return [(self.path / path) for path in self.project_config.third_party_module_dirs]

    @property
    @lru_cache()
    def modules_paths(self):
        # In fact core_modules_path is os.path.join(odoo.tools.config['root_path'], 'addons').
        # We don't want to import odoo. It's long one second almost.
        import importlib
        odoo_path = importlib.util.find_spec('odoo').submodule_search_locations[0]
        core_modules_path = pathlib.Path(odoo_path, 'addons').resolve()

        return (
            self.project_module_paths
            + self.third_party_module_paths
            + [core_modules_path]
        )

    def collect_modules(self, paths: Iterable[Path], exclude: Container[str] = ()):
        modules = ModuleSet()
        for module_path in paths:
            for subdir in module_path.iterdir():
                if subdir.name not in exclude and is_module(subdir):
                    modules.add(Module(subdir))
        return modules

    @lru_cache(maxsize=1024)
    def module(self, module_name):
        for modules_path in self.modules_paths:
            module_path = modules_path / module_name
            if is_module(module_path):
                # TODO Cache?
                return Module(module_path)
        raise LookupError(f'No module found: {module_name}')

    def find_modules(self, module_names):
        return ModuleSet(self.module(module_name) for module_name in module_names)

    @property
    def required_modules(self):
        if self.modules:
            return self.find_modules(self.modules)
        return (
            self.collect_modules(self.project_module_paths, exclude=self.project_config.exclude_modules)
            | self.find_modules(self.project_config.include_modules)
        )

    def expand_dependencies(self, modules):
        modules_to_check_depends = modules

        while True:
            module_depends_names = modules_to_check_depends.depends()
            if module_depends_names:
                modules_to_check_depends = self.find_modules(module_depends_names)
                modules |= modules_to_check_depends
            else:
                break

        return modules

    def auto_install_modules(self, modules: ModuleSet):
        auto_install_modules = ModuleSet()
        for module in self.collect_modules(self.modules_paths, exclude=modules.names()):
            if module.auto_install and set(module.depends) <= modules.names():
                auto_install_modules.add(module)
        return auto_install_modules

    @property
    def installed_modules(self):
        modules = self.expand_dependencies(self.required_modules)

        while True:
            auto_install_modules = self.auto_install_modules(modules)
            if auto_install_modules:
                modules |= auto_install_modules
            else:
                break

        return modules

    def topologic_dependencies(self, modules: ModuleSet):
        result = []
        visited = set()

        def visit(modd):
            if modd not in visited:
                visited.add(modd)
                if modd in modules:
                    for depend_module in self.find_modules(modd.depends).sorted():
                        visit(depend_module)
                    result.append(modd)

        for module in modules.sorted():
            visit(module)

        return result

    @lru_cache()
    def installed_modules_list(self, inversed=False):
        modules = self.topologic_dependencies(self.installed_modules)
        if inversed:
            modules = modules.reverse()
        return modules

    # =======================================================================

    # def field(self, module_name, model_name, field_name):
    #     module = self.module(module_name)
    #     field = Field()
    #     # for module in module.topological_depends():
    #     for module in self.topological_depends(module):
    #         for model_def in module.model_defs(model_name):
    #             for attr_def in model_def.attr_defs(field_name):
    #                 field.apply(attr_def)
    #     return field

    def topological_depends(self, module):
        # expanded_modules = self.expanded(module)
        graph = self.module_graph(module)
        return topologic(graph)

    def module_graph_OFF(self, module_name, processed_modules=set()):
        edges = []
        processed_modules.add(module_name)
        module = self.module(module_name)
        edges.extend([(module, depend_module) for depend_module in module.depends])
        for dependency_module_name in module.depends:
            if dependency_module_name not in processed_modules:
                edges.extend(self.module_graph(dependency_module_name, processed_modules))
        return edges

    def module_graph(self, module_name):
        processed_modules = set()

        def recursive_module_graph(module):
            edges = []
            processed_modules.add(module)
            for dependency_module_name in module.depends:
                dependency_module = self.module(dependency_module_name)
                edges.append((module, dependency_module))
                if dependency_module not in processed_modules:
                    edges.extend(self.module_graph(dependency_module))
            return edges

        return recursive_module_graph(self.module(module_name))

    # @lru_cache(maxsize=1024)
    # def module(self, module_name):
    #     return Module(self.module_path(module_name), module_name)

    def attr(self, model_name, attr_name, module=None):
        deps = self.module_dependencies(module_name)

    # ============= create db ====================
    # Copy of click_odoo_contrib/initdb.py:addons_hash
    def addons_hash(self, module_names, with_demo):
        h = hashlib.sha1()
        h.update("!demo={}!".format(int(bool(with_demo))).encode("utf8"))
        for module_name in sorted(module_names):
            module_path = self.module_path(module_name)
            h.update(module_name.encode("utf8"))
            for filepath in _walk(module_path):
                h.update(filepath.encode("utf8"))
                with open(os.path.join(module_path, filepath), "rb") as f:
                    h.update(f.read())
        return h.hexdigest()

    @lru_cache(maxsize=1024)
    def module_mtime(self, module_name):
        module_path = self.module_path(module_name)
        return max(os.path.getmtime(file_path) for file_path in _walk(module_path))

    def read_dependencies(self, module_names: set):
        for module_name in module_names:
            pass

    def cache_key(self, module_names, timestamp):
        module_mtime = {}
        for module_name in module_names:
            module_path = self.path(module_name)


    # Env
    # TODO Use functools.cached_property for Python3.8+
    @property
    @lru_cache(maxsize=1)
    def env(self):
        # Keep ref on generator force close generator later
        self._env_generator = self._get_env_generator()
        return next(self._env_generator)

    def _get_env_generator(self):
        import mock
        from odoo_commands.database_mock import CursorMock, FakeDatabase
        import odoo

        class CursorDbMock(CursorMock):
            db = FakeDatabase(self.installed_modules)

        # TODO Try other way
        odoo.modules.registry.Registry.in_test_mode = lambda self: True

        with mock.patch('odoo.sql_db.Cursor', CursorDbMock):
            with odoo.api.Environment.manage():
                with odoo.registry('soma').cursor() as cr:
                    print('2')
                    yield odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})

    # ========== Translation ==========
    def search_translation(self, tupl, lang=None):
        for module in self.installed_modules_list():
            translations = module.translations(lang or self.lang)
            if tupl in translations:
                return translations[tupl]

    def code_translation(self, file_path, value, lineno=None):
        # if not file_path.startswith('addons/'):
        #     file_path = f'addons/{file_path}'
        return self.search_translation(('code', file_path, lineno, value))

    def selection(self, model_name, field_name, value, lang=None):
        field = self.env[model_name]._fields[field_name]
        for selection_value, selection_string in field.selection:
            if value == selection_value:
                break
        else:
            raise ValueError('Invalid selection value')
        return self.search_translation(('selection', f'{model_name},{field_name}', '0', selection_string), lang=lang)

    def constraint(self, model, value):
        return self.search_translation(('constraint', model, '0', value))

    def sql_constraint(self, model, value):
        return self.search_translation(('sql_constraint', model, '0', value))

    def model_translation(self, model_name, field_name, xml_id, origin, lang=None):
        return self.search_translation(('model', f'{model_name},{field_name}', xml_id, origin), lang=lang)

    def model_description(self, model_name, lang=None):
        model = self.env[model_name]
        if not lang:
            return model._description
        xml_id = f'{model._module}.model_{model_name.replace(".", "_")}'
        return self.model_translation('ir.model', 'name', xml_id, model._description, lang=lang)

    # def field_description(self, module_name, model_name, field_name):
    def field_description(self, model_name, field_name, lang=None):
        field = self.env[model_name]._fields[field_name]
        if not lang:
            return field.string
        xml_id = f'{field._module}.field_{model_name.replace(".", "_")}_{field_name}'
        return self.model_translation('ir.model.fields', 'field_description', xml_id, field.string, lang=lang)
