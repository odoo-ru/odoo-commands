import collections
import logging

import astroid
from astroid import nodes

from odoo_commands.definitions import ModelDef

MODEL_ATTR_NAMES = {
    '_auto',
    '_rec_name',
    '_name',
    '_inherit',
    '_description',
    '_order',
}


ATTR_LITERALS = {
    nodes.Const,
    nodes.List,
    nodes.Tuple,
    nodes.Dict,
    nodes.BinOp,
    nodes.UnaryOp,
}

POSITION_ARGS = {
    'Float': ('string', 'digits'),
    'Monetary': ('string', 'currency_field'),
    'Selection': ('selection', 'string'),
    'Many2one': ('comodel_name', 'string'),
    'One2many': ('comodel_name', 'inverse_name', 'string'),
    'Many2many': ('comodel_name', 'relation', 'column1', 'column2', 'string'),
}


IMPORT_NODES = {
    nodes.ImportFrom,
    nodes.Import,
}
MODULE_SKIP_NODES = {
    nodes.FunctionDef,
    nodes.ClassDef,
    nodes.AugAssign,
    nodes.Expr,
    nodes.TryExcept,
    nodes.If,
}
MODEL_SKIP_NODES = {
    nodes.FunctionDef,
}

logger = logging.getLogger(__name__)


def parse_python_module(path):
    # print(path)
    global_literals = {}
    with open(path) as python_file:
        python_module = astroid.parse(python_file.read(), path=path)
        for node in python_module.body:
            # if isinstance(node, ImportNode):
            node_type = type(node)
            if node_type in IMPORT_NODES:
                continue
            elif node_type is nodes.Assign:
                exec_assign(node.as_string(), {}, global_literals)
            elif is_model(node):
                yield parse_model(node, global_literals)
            elif node_type in MODULE_SKIP_NODES:
                continue
            else:
                raise ZeroDivisionError()
                logger.warning('Global skip: %s', node.as_string())



MODEL_BASE_NAMES = {'models.' + class_name for class_name in {
    'BaseModel',
    'AbstractModel',
    'Model',
    'TransientModel',
}}

def is_model(node):
    return isinstance(node, nodes.ClassDef) and any(base_name in MODEL_BASE_NAMES for base_name in node.basenames)


def exec_assign(expression, global_scope, local_scope):
    try:
        exec(expression, global_scope, local_scope)
    except NameError:
        logger.warning('exec_assign: %s', expression)


    def SOMA(cls, node: nodes.Assign):
        if len(node.targets) != 1:
            logger.warning('Assignment %s', node.as_string())
            return

        if not isinstance(node.targets[0], nodes.AssignName):
            logger.warning('Not assign name: %s', node.as_string())
            return

        attr_name = node.targets[0].name
        # if attr_name in cls.MODEL_ATTR_NAMES:
        if attr_name[0] == '_':
            # if isinstance(node.value, nodes.Const):
            if type(node.value) in cls.ATTR_LITERALS:
                cls._parse_attr_assignment(attr_name, node.value)
            else:
                logger.warning('Skip value parsing: %s', node.as_string())
        elif isinstance(node.value, nodes.Call):
            # return attr_name, cls._parse_field_assignment(node)
            cls._parse_field_assignment(attr_name, node.value)


def parse_model(class_def: nodes.ClassDef, global_scope):
    local_scope = collections.OrderedDict()

    for node in class_def.body:
        node_type = type(node)
        if isinstance(node, nodes.Assign):
            exec_assign(node.as_string(), global_scope, local_scope)
        elif node_type in MODEL_SKIP_NODES:
            continue
        else:
            raise ZeroDivisionError
            logger.warning('model skip: %s', node.as_string())

    return ModelDef(local_scope)


def parse_assignment(node: nodes.Assign):
    if len(node.targets) != 1:
        logger.warning('Assignment %s', node.as_string())
        return

    if not isinstance(node.targets[0], nodes.AssignName):
        logger.warning('Not assign name: %s', node.as_string())
        return

    attr_name = node.targets[0].name
    # if attr_name in cls.MODEL_ATTR_NAMES:
    if attr_name[0] == '_':
        # if isinstance(node.value, nodes.Const):
        if type(node.value) in cls.ATTR_LITERALS:
            cls._parse_attr_assignment(attr_name, node.value)
        else:
            logger.warning('Skip value parsing: %s', node.as_string())
    elif isinstance(node.value, nodes.Call):
        # return attr_name, cls._parse_field_assignment(node)
        cls._parse_field_assignment(attr_name, node.value)

    else:
        logger.warning('Skip model code: %s', node.as_string())

def _parse_attr_assignment(self, name, node: ATTR_LITERALS):
    # if node.name == 'str':
    #     self[name] = node.value
    # else:
    #     logger.warning('Skip value parsing: %s', node.as_string())
    if type(node) in self.ATTR_LITERALS:
        # return self.eval_literal(node.as_string())
        self[name] = self.eval_literal(node.as_string())
    else:
        logger.warning('Skip value parsing: %s', node.as_string())

@staticmethod
def eval_literal(expression):
    try:
        return eval(expression, {}, {})
    except NameError:
        logger.warning('Unparsable: %s', expression)
        return Unparsable(expression)

# @classmethod
def _parse_field_assignment(cls, name, node: nodes.Call):
    func = node.func.as_string()
    try:
        fields_literal, field_class_name = func.split('.')
    except BaseException:
        logger.warning('Skip call: %s', node.as_string())
        return

    if fields_literal != 'fields':
        logger.warning('Skip call: %s', node.as_string())
        return

    NODE_CLASS_PARSER = {
        # nodes.Const: lambda node: node.value,
        nodes.Name: lambda node: Name(node.name),
        nodes.Attribute: lambda node: Name(node.as_string()),
        # nodes.List: lambda node: eval_const(node.as_string()),
        nodes.Lambda: lambda node: Lambda(node.as_string()),
        nodes.Call: lambda node: Call(node.as_string()),
        # Other
        nodes.Subscript: lambda node: Other(node.as_string()),
    }
    LITERALS = {
        nodes.Const,
        nodes.List,
        nodes.Tuple,
        nodes.Dict,
        nodes.BinOp,
        nodes.UnaryOp,
    }

    def eval_node(node):
        node_class = type(node)
        if node_class in LITERALS:
            return cls.eval_literal(node.as_string())
        elif node_class in NODE_CLASS_PARSER:
            parser = NODE_CLASS_PARSER.get(node_class)
            if parser:
                return parser(node)
        # if isinstance(node, nodes.Const):
        #     return node.value
        # elif isinstance(node, nodes.Name):
        #     return Name(node.name)
        # elif isinstance(node, nodes.List):
        #     return eval_const(node.as_string())
        else:
            raise ZeroDivisionError
            logger.warning('eval_node imposible: %s', node.as_string())
            return None
        # return eval(node, {}, {})

    def parse_arg(name, node):
        if name == 'domain':
            value = node.as_string()
        else:
            value = eval_node(node)
        return name, value

    field_args = {}
    if node.args:
        positional_arg_names = cls.POSITION_ARGS.get(field_class_name, ['string'])
        if len(node.args) > len(positional_arg_names):
            logger.warning('Skip too many positional arguments: %s', node.as_string())
            return

        field_args.update(
            # zip(positional_arg_names, (eval_node(arg) for arg in node.args)),
            parse_arg(*item) for item in zip(positional_arg_names, node.args)
        )

    field_args.update(
        # (keyword.arg, eval_node(keyword.value)) for keyword in node.keywords
        parse_arg(keyword.arg, keyword.value) for keyword in node.keywords
    )

    cls[name] = FieldDef(field_class_name, **field_args)
    # return FieldDef(field_class_name, **field_args)
