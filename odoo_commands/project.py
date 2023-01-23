import ast
import os
import pathlib
from functools import lru_cache
from typing import List, Set


class Module:
    # __slots__ = ('path', 'name')
    # sequence = 100

    def __init__(self, project, name, path):
        self.project = project
        self.name = name
        self.path = pathlib.Path(path)

    @property
    @lru_cache(maxsize=None)
    def manifest(self):
    # @property
    # @lru_cache(1024)
    # def manifest(self):
        # module_dir = self.module_path(module_name)
        manifest_path = os.path.join(self.path, '__manifest__.py')
        # if not os.path.isfile(manifest_path):
        #     raise FileNotFoundError("No Odoo manifest found in %s" % addon_dir)
        with open(manifest_path) as manifest_file:
            return ast.literal_eval(manifest_file.read())
        # attrs.setdefault('sequence', 100)
        # if not attrs.get('depends'):
        #     attrs['depends'] = ['base']
        self.attrs = attrs

        if self.name == 'base':
            self.depends = []
        else:
            depends = attrs.get('depends')
            self.depends = depends if depends else ['base']

    def data_file_path(self):
        yield from self.manifest.get('data', [])

    @property
    @lru_cache(maxsize=None)
    def expanded_dependencies(self):
        if self.name == 'base':
            return {}

        depends = self.manifest.get('depends')
        if not depends:
            depends = ['base']

        res = {}
        for depend in depends:
            module = self.project.module(depend)
            res[depend] = module
            res.update(module.expanded_dependencies)

        return res

    # def topological_depends(self):
    #     graph = nx.DiGraph()
    #     return list(nx.lexicographical_topological_sort(graph, key=lambda module: module.sequence))


class Model:
    pass


class Field:
    def __init__(self):
        self.name = ''


class OdooProject:
    def __init__(self, project_module_paths):
        self.project_modules_paths = project_module_paths
        # self.cache = {}
        self.core_module_path = None

    @property
    @lru_cache()
    def modules_paths(self):
        import odoo
        core_modules_path = pathlib.Path(odoo.tools.config['root_path'], 'addons')
        return list(map(pathlib.Path, self.project_modules_paths)) + [core_modules_path]

    @lru_cache(maxsize=1024)
    def module(self, module_name):
        for modules_path in self.modules_paths:
            module_path = os.path.join(modules_path, module_name)
            if os.path.isdir(module_path) and os.path.isfile(os.path.join(module_path, '__manifest__.py')):
                return Module(self, module_name, module_path)

        raise LookupError(f'No module found: {module_name}')

    def field(self, module_name, model_name, field_name):
        module = self.module(module_name)
        field = Field()
        # for module in module.topological_depends():
        for module in self.topological_depends(module):
            for model_def in module.model_defs(model_name):
                for attr_def in model_def.attr_defs(field_name):
                    field.apply(attr_def)
        return field

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
    def init_database(self, module_names: Set[str]):
        timestamps = test_time()
        self.install_modules(modules, timestamps)

    def install_modules(self, modules, timestamps=None):
        timestamp = timestamps[0]
        timestamp_modules, hash = sub(modules, timestamp)
        # hash = hash(timestamp_modules)
        if db(hash):
            return db(hash)
        else:
            d = self.install_modules(timestamp_modules, timestamps[1:])
            return init(d, modules - timestamp_modules)


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




    # def modules_cache(self, timestamp):
        # to_install + their deps - their unwanted deps - old modules - their deps



# project = OdooProject()
# module = project.module('soma')
# module.field['sale.order', 'name'].translate
#
# project.field['soma', 'sale.order', 'name']
