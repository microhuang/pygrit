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
