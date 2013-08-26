#
# lazy loading decorator and class, idea stolen from ruby's lazy class and
# http://stackoverflow.com/questions/3012421/python-lazy-property-decorator
#

#
# lazy loading decorator for class property
#
def lazyprop(fn):

    attr_name = '_' + fn.__name__

    @property
    def _lazyprop(inst):
        if not inst._loaded:
            obj = inst.lazy_source()
            inst.__dict__.update(obj.__dict__)
            # setattr(inst, '_loaded', True)
        return getattr(inst, attr_name)

    return _lazyprop


#
# Lazy class, for lazy object, add @lazyprop decorator to properties.
# Note that class must have `lazy_source` implemented to load real data
#
class Lazy(object):

    _loaded = False

    def __init__(self):
        self._loaded = True

    def lazy_source(self):
        raise NotImplementedError()

    @classmethod
    def create(klass):
        inst = klass.__new__(klass)
        inst._loaded = False
        return inst

#
# example
#

# class Foo(Lazy):

#     def __init__(self, name):
#         super(Foo, self).__init__()
#         self._name = name

#     @lazyprop
#     def name(self):
#         return self._name

#     def lazy_source(self):
#         # do some heavy loading here
#         return Foo.load_data()

#     @staticmethod
#     def load_data():
#         # real loading function
#         foo = Foo(name='foo')
#         return foo
