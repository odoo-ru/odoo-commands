import functools
from functools import cached_property


# https://stackoverflow.com/questions/798442/what-is-the-correct-or-best-way-to-subclass-the-python-set-class-adding-a-new
def wrap(method):
    @functools.wraps(method)
    def wrapped_method(*args, **kwargs):
        return OdooModuleSet(method(*args, **kwargs))
    return wrapped_method


class OdooModuleSet(set):
    @cached_property
    def names_list(self):
        return sorted(module.name for module in self)

    @cached_property
    def names(self):
        return {module.name for module in self}

    def depends(self):
        return set().union(*[module.depends for module in self]) - self.names

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
