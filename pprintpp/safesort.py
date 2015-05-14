import sys
import textwrap
import functools

PY3 = (sys.version_info >= (3, 0, 0))

def memoized_property(f):
    @functools.wraps(f)
    def memoized_property_helper(self):
        val = f(self)
        self.__dict__[f.__name__] = val
        return val
    return property(memoized_property_helper)

def _build_safe_cmp_func(name, cmp, prefix=""):
    code = textwrap.dedent("""\
        def {name}(self, other):
            try:
                return {prefix}(self.obj {cmp} other.obj)
            except TypeError:
                pass
            try:
                return {prefix}(self.safeobj {cmp} other.safeobj)
            except TypeError:
                pass
            return {prefix}(self.verysafeobj {cmp} other.verysafeobj)
    """).format(name=name, cmp=cmp, prefix=prefix)
    gs = ls = {}
    exec(code, gs, ls)
    return gs[name]

class SafelySortable(object):
    def __init__(self, obj, key=None):
        self.obj = (
            obj if key is None else
            key(obj)
        )

    @memoized_property
    def prefix(self):
        if PY3:
            return tuple(t.__name__ for t in type(self.obj).__mro__)
        return type(self.obj).__mro__

    @memoized_property
    def safeobj(self):
        return (self.prefix, self.obj)

    @memoized_property
    def verysafeobj(self):
        return (self.prefix, id(self.obj))

    def __hash__(self):
        # TODO: is this a good idea? Maybe this should not exist?
        try:
            return hash(self.obj)
        except TypeError:
            pass
        return 1

    __lt__ = _build_safe_cmp_func("__lt__", "<")
    __gt__ = _build_safe_cmp_func("__gt__", ">")
    __le__ = _build_safe_cmp_func("__le__", "<=")
    __ge__ = _build_safe_cmp_func("__ge__", ">=")
    __eq__ = _build_safe_cmp_func("__eq__", "==")
    __ne__ = _build_safe_cmp_func("__ne__", "!=")
    __cmp__ = _build_safe_cmp_func("__cmp__", ",", "cmp")


def safesort(input, key=None, reverse=False):
    """ Safely sort heterogeneous collections. """
    # TODO: support cmp= on Py 2.x?
    return sorted(input, key=lambda o: SafelySortable(o, key=key), reverse=reverse)
