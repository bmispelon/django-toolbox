from functools import partial, wraps

def wrapped_partial(func, *args, **keywords):
    """Return a wrapped partial function.
    Used for wrapping view functions so that __name__, __doc__ and __module__ are preserved.
    
    """
    newfunc = partial(func, *args, **keywords)
    return wraps(func)(newfunc)
