
def conditional(condition, decorator):
    if condition:
        return decorator
    else:
        return lambda fn: fn
