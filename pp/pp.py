import sys
import types


class pp_magic_module(types.ModuleType):
    original_module = sys.modules[__name__]
    __file__ = original_module.__file__
    __package__ = original_module.__package__

    def __init__(self):
        types.ModuleType.__init__(self, __name__)
        try:
            import pprintpp as pprint_mod
        except ImportError:
            import pprint as pprint_mod
        self._set_mod(pprint_mod)

    def _set_mod(self, mod):
        self.pprint_mod = mod
        type_dict = type(self).__dict__
        for name in dir(mod):
            if name in type_dict or name.startswith("_"):
                continue
            setattr(self, name, getattr(mod, name))
        self.__doc__ = mod.__doc__

    def __call__(self, *args, **kwargs):
        return self.pprint(*args, **kwargs)

    def fmt(self, *args, **kwargs):
        return self.pformat(*args, **kwargs)

    def __repr__(self):
        return "<module '%s' (pp_magic_module with pprint_mod=%r)>" %(
            self.__name__,
            self.pprint_mod.__name__,
        )


sys.modules[__name__] = pp_magic_module()
