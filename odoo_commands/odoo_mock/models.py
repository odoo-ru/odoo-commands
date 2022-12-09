LOG_ACCESS_COLUMNS = ['create_uid', 'create_date', 'write_uid', 'write_date']
MAGIC_COLUMNS = ['id'] + LOG_ACCESS_COLUMNS

class MetaModel:
    pass

class Model:
    # Fix absent attr for setattr global to IrRule
    _module = None
    pass

class BaseModel:
    def _check_recursion(self):
        pass

class TransientModel(Model):
    pass


class AbstractModel(Model):
    pass


check_method_name = None
def check_method_name_OFF(name):
    """ Raise an ``AccessError`` if ``name`` is a private method name. """
    if regex_private.match(name):
        raise AccessError(_('Private methods (such as %s) cannot be called remotely.') % (name,))
