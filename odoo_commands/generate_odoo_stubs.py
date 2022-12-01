import pathlib
import logging

import astroid
from astroid import nodes

logger = logging.getLogger(__name__)


def is_simple_assignment(node: nodes.Assign):
    if len(node.targets) == 1:
        return


class ModelDef:
    MODEL_ATTR_NAMES = {
        '_name',
        '_inherit',
        '_description',
        '_order',
    }

    POSITION_ARGS = {
        'Float': ('string', 'digits'),
        'Monetary': ('string', 'currency_field'),
        'Selection': ('selection', 'string'),
        'Many2one': ('comodel_name', 'string'),
        'One2many': ('comodel_name', 'inverse_name', 'string'),
        'Many2many': ('comodel_name', 'relation', 'column1', 'column2', 'string'),
    }

    # def __init__(self, node: nodes.ClassDef):
    def __init__(self, vals):
        # self.node = node
        # self.parse(node)
        self.vals = vals

    @classmethod
    def parse(self, class_def: nodes.ClassDef):
        vals = {}
        for node in class_def.body:
            if isinstance(node, nodes.Assign):
                vals.update(self._parse_assignment(node))
        return ModelDef(vals)

    @classmethod
    def _parse_assignment(cls, node: nodes.Assign):
        # vals = {}

        if len(node.targets) != 1:
            logger.warning('Assignment %s', node.as_string())
            return

        attr_name = node.targets[0].name
        if attr_name in cls.MODEL_ATTR_NAMES:
            if isinstance(node.value, nodes.Const):
                if node.value.name == 'str':
                    value = node.value.value
                else:
                    value = None
                    logger.warning('Skip value parsing: %s', node.as_string())

                if value is not None:
                    return attr_name.lstrip('_'), value
            else:
                logger.warning('Skip value parsing: %s', node.as_string())
        elif isinstance(node.value, nodes.Call):
            return cls._parse_field_assignment(node)

        # else:
        logger.warning('Skip attr: %s', node.as_string())

    @classmethod
    def _parse_field_assignment(cls, node: nodes.Call):
        func = node.func.as_string()
        try:
            fields_literal, field_class_name = func.split('.')
        except BaseException:
            logger.warning('Skip call: %s', node.as_string())
            return

        if fields_literal != 'fields':
            logger.warning('Skip call: %s', node.as_string())
            return




def is_odoo_module(path):
    if isinstance(path, str):
        path = pathlib.Path(path)
    return path.is_dir() and (path / '__manifest__.py').is_file()

MODEL_BASE_NAMES = {'models.' + class_name for class_name in {
    'BaseModel',
    'AbstractModel',
    'Model',
    'TransientModel',
}}

def is_model(node):
    return isinstance(node, nodes.ClassDef) and any(base_name in MODEL_BASE_NAMES for base_name in node.basenames)


def parse_module(module_path):
    global g
    for path in module_path.glob('**/*.py'):
        with open(path) as python_file:
            python_module = astroid.parse(python_file.read(), path=path)
            for node in python_module.values():
                # print(node)
                if is_model(node):
                    return node
                    # return ModelDef.parse(node)
                    # yield node


def generate(modules_path):
    for path in pathlib.Path(modules_path).iterdir():
        if is_odoo_module(path):
            return parse_module(path)
            # for model_def in iter_models(path):
            #     return model_def


# m = parse_module('tests/addons')
path = '/home/voronin/.local/share/virtualenvs/ruchet-SAKa37C1/lib/python3.6/site-packages/odoo/addons/base'
m = parse_module(pathlib.Path(path))
