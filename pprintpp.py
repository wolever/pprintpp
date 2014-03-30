import os
import ast
import sys
import warnings

from cStringIO import StringIO

__all__ = [
    "pprint", "pformat", "isreadable", "isrecursive", "saferepr",
    "PrettyPrinter",
]


def pprint(object, stream=None, indent=4, width=80, depth=None):
    """Pretty-print a Python object to a stream [default is sys.stdout]."""
    printer = PrettyPrinter(
        stream=stream, indent=indent, width=width, depth=depth)
    printer.pprint(object)

def pformat(object, indent=4, width=80, depth=None):
    """Format a Python object into a pretty-printed representation."""
    return PrettyPrinter(indent=indent, width=width, depth=depth).pformat(object)

def saferepr(object):
    """Version of repr() which can handle recursive data structures."""
    return PrettyPrinter().pformat(object)

def isreadable(object):
    """Determine if saferepr(object) is readable by eval()."""
    return PrettyPrinter().isreadable(object)

def isrecursive(object):
    """Determine if object requires a recursive representation."""
    return PrettyPrinter().isrecursive(object)

def _sorted(iterable):
    with warnings.catch_warnings():
        if sys.py3kwarning:
            warnings.filterwarnings("ignore", "comparing unequal types "
                                    "not supported", DeprecationWarning)
        return sorted(iterable)

def console(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv) != 1:
        name = argv[0]
        if name.startswith("/"):
            name = os.path.basename(name)
        print "Usage: %s" %(argv[0], )
        print
        print "Pipe Python literals into %s to pretty-print them" %(argv[0], )
        return 1
    obj = ast.literal_eval(sys.stdin.read().strip())
    pprint(obj)
    return 0

def monkeypatch(mod=None):
    if "pprint" in sys.modules:
        warnings.warn("'pprint' has already been imported; monkeypatching "
                      "won't work everywhere.")
    import pprint
    sys.modules["pprint_original"] = pprint
    sys.modules["pprint"] = mod or sys.modules["pprintpp"]

class PPrintSharedState(object):
    recursive = False
    readable = True
    cur_line_length = 0

    def clone(self):
        new = type(self)()
        new.__dict__.update(self.__dict__)
        return new


class PPrintState(object):
    indent = 4
    level = 0
    max_width = 80
    max_depth = None
    stream = None
    context = None
    write_constrain = None

    class WriteConstrained(Exception):
        pass

    def __init__(self, **attrs):
        self.__dict__.update(attrs)
        self.s = PPrintSharedState()

    def assert_sanity(self):
        assert self.indent >= 0, "indent must be >= 0"
        assert self.max_depth is None or self.max_depth > 0, "depth must be > 0"
        assert self.max_width, "width must be != 0"

    def replace(self, **attrs):
        new_state = type(self)()
        new_state.__dict__.update(self.__dict__)
        new_state.__dict__.update(attrs)
        new_state.context = dict(new_state.context)
        new_state.s = self.s
        return new_state

    def clone(self, clone_shared=False):
        new = self.replace()
        if clone_shared:
            new.s = self.s.clone()
        return new

    def write(self, bytes):
        if self.write_constrain is not None:
            self.write_constrain -= len(bytes)
            if self.write_constrain < 0:
                raise self.WriteConstrained

        self.stream.write(bytes)
        nl_idx = bytes.rfind("\n")
        if nl_idx < 0:
            self.s.cur_line_length += len(bytes)
        else:
            self.s.cur_line_length = len(bytes) - (nl_idx + 1)

    def get_indent_string(self):
        return (self.level * self.indent) * " "



class PrettyPrinter(object):
    def __init__(self, indent=4, width=80, depth=None, stream=None):
        """Handle pretty printing operations onto a stream using a set of
        configured parameters.

        indent
            Number of spaces to indent for each level of nesting.

        width
            Attempted maximum number of columns in the output.

        depth
            The maximum depth to print out nested structures.

        stream
            The desired output stream.  If omitted (or false), the standard
            output stream available at construction will be used.

        """
        self.get_default_state = lambda: PPrintState(
            indent=int(indent),
            max_width=int(width),
            stream=stream or sys.stdout,
            context={},
        )
        self.get_default_state().assert_sanity()

    def pprint(self, object, state=None):
        state = state or self.get_default_state()
        self._format(object, state)
        state.write("\n")

    def pformat(self, object, state=None):
        sio = StringIO()
        state = state or self.get_default_state()
        state = state.replace(stream=sio)
        self._format(object, state)
        return sio.getvalue()

    def isrecursive(self, object):
        state = self.get_default_state()
        self._format(object, state)
        return state.s.recursive

    def isreadable(self, object):
        state = self.get_default_state()
        self._format(object, state)
        return state.s.readable and not state.s.recursive

    _listish_reprs = {
        list.__repr__: ("list", "[", "]", "[]"),
        tuple.__repr__: ("tuple", "(", ")", "()"),
        set.__repr__: ("set", "set([", "])", "set()"),
        frozenset.__repr__: ("set", "frozenset([", "])", "frozenset()"),
    }

    def _format_nested_objects(self, object, sub_objects, state, typeish=None):
        objid = id(object)
        state.level += 1
        state.context[objid] = 1
        try:
            # First, try to fit everything on one line. For simplicity, assume
            # that it takes three characters to close the object (ex, `]),`)
            oneline_state = state.clone(clone_shared=True)
            oneline_state.stream = StringIO()
            oneline_state.write_constrain = (
                state.max_width - state.s.cur_line_length - 3
            )
            try:
                self._write_nested_real(sub_objects, oneline_state, typeish,
                                        oneline=True)
                state.write(oneline_state.stream.getvalue())
                return
            except oneline_state.WriteConstrained:
                pass
            state.write("\n" + state.get_indent_string())
            self._write_nested_real(sub_objects, state, typeish)
        finally:
            state.level -= 1
        state.write(state.get_indent_string())

    def _write_nested_real(self, sub_objects, state, typeish, oneline=False):
        indent_str = state.get_indent_string()
        first = True
        joiner = oneline and ", " or ",\n" + indent_str
        sorted_sub_objects = _sorted(sub_objects)
        if typeish == "dict":
            for k, v in sorted_sub_objects:
                if first:
                    first = False
                else:
                    state.write(joiner)
                self._format(k, state)
                state.write(": ")
                self._format(v, state)
        else:
            for o in sorted_sub_objects:
                if first:
                    first = False
                else:
                    state.write(joiner)
                self._format(o, state)
        if oneline and typeish == "tuple" and len(sub_objects) == 1:
            state.write(", ")
        elif not oneline:
            state.write(",\n")

    def _format(self, object, state):
        write = state.write
        if state.max_depth and state.level >= state.max_depth:
            write("...")
            return
        state = state.clone()
        objid = id(object)
        if objid in state.context:
            write(self._recursion(object, state))
            return

        typ = type(object)
        r = getattr(typ, "__repr__", None)
        if r is dict.__repr__:
            if not len(object):
                write('{}')
                return
            write('{')
            self._format_nested_objects(object, object.items(),
                                        state, typeish="dict")
            write("}")
            return

        opener_closer_empty = self._listish_reprs.get(r)
        if opener_closer_empty is not None:
            typeish, opener, closer, empty = opener_closer_empty
            length = len(object)

            if length == 0:
                write(empty)
                return

            write(opener)
            self._format_nested_objects(object, object, state, typeish=typeish)
            write(closer)
            return

        is_uni = r == unicode.__repr__
        if r == str.__repr__ or is_uni:
            if 'locale' not in sys.modules:
                write(repr(object))
                return

            if "'" in object and '"' not in object:
                quote = '"'
                quotes = {'"': '\\"'}
            else:
                quote = "'"
                quotes = {"'": "\\'"}
            qget = quotes.get
            pslice = is_uni and 2 or 1
            write(is_uni and 'u' or '' + quote)
            for char in object:
                if char.isalpha():
                    write(char)
                else:
                    write(qget(char) or repr(char)[pslice:-1])
            write(quote)
            return

        orepr = repr(object)
        state.s.readable = (
            state.s.readable and
            not orepr.startswith("<")
        )
        write(orepr)
        return

    def _repr(self, object, context, level):
        repr, readable, recursive = self.format(object, context.copy(),
                                                self._depth, level)
        if not readable:
            self._readable = False
        if recursive:
            self._recursive = True
        return repr

    def format(self, object, context, maxlevels, level):
        """Format object for a specific context, returning a string
        and flags indicating whether the representation is 'readable'
        and whether the object represents a recursive construct.
        """
        state = self.get_default_state()
        result = self.pformat(object, state=state)
        return result, state.s.readable, state.s.recursive

    def _recursion(self, object, state):
        state.s.recursive = True
        return ("<Recursion on %s with id=%s>"
                % (type(object).__name__, id(object)))


if __name__ == "__main__":
    #sys.exit(console())
    somelist = [1,2,3]
    recursive = []
    recursive.extend([recursive, recursive, recursive])
    pprint({
        "a": {"a": "b"},
        "b": [somelist, somelist],
        "c": (1, ),
        "d": (1,2,3),
        "recursive": recursive,
        "z": {
            "very very very long key stuff 1234": {
                "much value": "very nest! " * 10,
                u"unicode": u"4U!'\"",
            },
            "aldksfj alskfj askfjas fkjasdlkf jasdlkf ajslfjas": ["asdf"] * 10,
        },
    })
