def attrsetter(attr, value):
    """ Return a function that sets ``attr`` on its argument and returns it. """
    return lambda method: setattr(method, attr, value) or method

def model(method):
    method._api = 'model'
    return method

def model_cr(method):
    method._api = 'model_cr'
    return method

def multi(method):
    method._api = 'multi'
    return method

def depends(*args):
    if args and callable(args[0]):
        args = args[0]
    elif any('id' in arg.split('.') for arg in args):
        raise NotImplementedError("Compute method cannot depend on field 'id'.")
    return attrsetter('_depends', args)

def onchange(*args):
    return attrsetter('_onchange', args)

def constrains(*args):
    return attrsetter('_constrains', args)

def returns(model, downgrade=None, upgrade=None):
    return attrsetter('_returns', (model, downgrade, upgrade))
