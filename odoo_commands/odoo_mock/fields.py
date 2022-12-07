
# __all__ = {
#     'Char',
# }
s = """
Field
    string

Id
Boolean
Integer
Date
Datetime
Binary
Reference

Float
    string, digits
Monetary
    string, currency_field

_String
    string
Char(_String)
Text(_String)
Html(_String)

Selection
    selection, string

_Relational
Many2one(_Relational)
    comodel_name, string

_RelationalMulti(_Relational)
One2many(_RelationalMulti)
    comodel_name, inverse_name, string
Many2many(_RelationalMulti)
    comodel_name, relation, column1, column2, string
"""

class Default:
    pass


class Field:
    def __init__(self, string=Default, **kwargs):
        kwargs['string'] = string
        for name, value in kwargs.items():
            setattr(self, name, value)


class Boolean(Field):
    pass


class Integer(Field):
    pass


class Date(Field):
    def today(self):
        pass

    def context_today(self):
        pass


class Datetime(Field):
    def now(self):
        pass


class Binary(Field):
    pass


class Reference(Field):
    pass


class Char(Field):
    pass


class Text(Field):
    pass


class Html(Field):
    pass


class Float(Field):
    def __init__(self, string=Default, digits=Default, **kwargs):
        super().__init__(string=string, _digits=digits, **kwargs)


class Monetary(Field):
    def __init__(self, string=Default, currency_field=Default, **kwargs):
        super().__init__(string=string, currency_field=currency_field, **kwargs)


class Selection(Field):
    def __init__(self, selection=Default, string=Default, **kwargs):
        super().__init__(selection=selection, string=string, **kwargs)


class Many2one(Field):
    def __init__(self, comodel_name=Default, string=Default, **kwargs):
        super().__init__(comodel_name=comodel_name, string=string, **kwargs)


class Many2many(Field):
    def __init__(self, comodel_name=Default, relation=Default, column1=Default, column2=Default, string=Default,
                 **kwargs):
        super().__init__(comodel_name=comodel_name, relation=relation, column1=column1, column2=column2, string=string,
                         **kwargs)


class One2many(Field):
    def __init__(self, comodel_name=Default, inverse_name=Default, string=Default, **kwargs):
        super().__init__(comodel_name=comodel_name, inverse_name=inverse_name, string=string, **kwargs)
