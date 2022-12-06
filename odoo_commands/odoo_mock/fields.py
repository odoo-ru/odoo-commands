
# __all__ = {
#     'Char',
# }

class Default:
    pass


class FieldDef:
    def __init__(self, string=Default, **kwargs):
        pass


def field(**kwargs):
    return FieldDef


Char = field(string=Default)
