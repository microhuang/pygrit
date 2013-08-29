# -*- coding: utf-8 -*-

import functools

def cached(func):
    cache = {}

    def template(*args):
        key = (func, ) + args
        try:
            ret = cache[key]
        except KeyError:
            ret = func(*args)
            cache[key] = ret
        else:
            pass
        return ret
    functools.update_wrapper(template, func)
    return template

def should_in_git_python(func):
    """
    warn developer, that decorated function should be written
    in git-python module
    """
    def log(*args, **kwargs):
        from pygrit import logger
        logger.warn("%s should be writtten in git-python." % func.__name__)
        return func(*args, **kwargs)
    functools.update_wrapper(log, func)
    return log

def deprecated(func):
    """
    warn developer, that decorated function should not be used any more
    """
    def log(*args, **kwargs):
        from pygrit import logger
        logger.warn("%s is deprecated, it would be REMOVED soon." % func.__name__)
        return func(*args, **kwargs)
    functools.update_wrapper(log, func)
    return log
