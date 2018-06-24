from __future__ import print_function

import io
import os
import ast
import sys
import warnings
import unicodedata

__all__ = [
    "pprint", "pformat", "isreadable", "isrecursive", "saferepr",
    "PrettyPrinter",
]


#
# Py2/Py3 compatibility stuff
#

try:
    from collections import OrderedDict, defaultdict, Counter
    _test_has_collections = True
except ImportError:
    # Python 2.6 doesn't have collections
    class dummy_class(object):
        __repr__ = object()
    OrderedDict = defaultdict = Counter = dummy_class
    _test_has_collections = False


PY3 = sys.version_info >= (3, 0, 0)
BytesType = bytes
TextType = str if PY3 else unicode
u_prefix = '' if PY3 else 'u'


if PY3:
    # Import builins explicitly to keep Py2 static analyzers happy
    import builtins
    chr_to_ascii = lambda x: builtins.ascii(x)[1:-1]
    unichr = chr
    from .safesort import safesort
    _iteritems = lambda x: x.items()
else:
    chr_to_ascii = lambda x: repr(x)[2:-1]
    safesort = sorted
    _iteritems = lambda x: x.iteritems()


def _sorted_py2(iterable):
    with warnings.catch_warnings():
        if getattr(sys, "py3kwarning", False):
            warnings.filterwarnings("ignore", "comparing unequal types "
                                    "not supported", DeprecationWarning)
        return sorted(iterable)

def _sorted_py3(iterable):
    try:
        return sorted(iterable)
    except TypeError:
        return safesort(iterable)

_sorted = PY3 and _sorted_py3 or _sorted_py3

#
# End compatibility stuff
#

class TextIO(io.TextIOWrapper):
    def __init__(self, encoding=None):
        io.TextIOWrapper.__init__(self, io.BytesIO(), encoding=encoding)

    def getvalue(self):
        self.flush()
        return self.buffer.getvalue().decode(self.encoding)


# pprintpp will make an attempt to print as many Unicode characters as is
# safely possible. It will use the character category along with this table to
# determine whether or not it is safe to print a character. In this context,
# "safety" is defined as "the character will appear visually distinct" -
# combining characters, spaces, and other things which could be visually
# ambiguous are repr'd, others will be printed. I made this table mostly by
# hand, mostly guessing, so please file bugs.
# Source: http://www.unicode.org/reports/tr44/#GC_Values_Table
unicode_printable_categories = {
    "Lu": 1, # Uppercase_Letter	an uppercase letter
    "Ll": 1, # Lowercase_Letter	a lowercase letter
    "Lt": 1, # Titlecase_Letter	a digraphic character, with first part uppercase
    "LC": 1, # Cased_Letter	Lu | Ll | Lt
    "Lm": 0, # Modifier_Letter	a modifier letter
    "Lo": 1, # Other_Letter	other letters, including syllables and ideographs
    "L":  1, # Letter	Lu | Ll | Lt | Lm | Lo
    "Mn": 0, # Nonspacing_Mark	a nonspacing combining mark (zero advance width)
    "Mc": 0, # Spacing_Mark	a spacing combining mark (positive advance width)
    "Me": 0, # Enclosing_Mark	an enclosing combining mark
    "M":  1, # Mark	Mn | Mc | Me
    "Nd": 1, # Decimal_Number	a decimal digit
    "Nl": 1, # Letter_Number	a letterlike numeric character
    "No": 1, # Other_Number	a numeric character of other type
    "N":  1, # Number	Nd | Nl | No
    "Pc": 1, # Connector_Punctuation	a connecting punctuation mark, like a tie
    "Pd": 1, # Dash_Punctuation	a dash or hyphen punctuation mark
    "Ps": 1, # Open_Punctuation	an opening punctuation mark (of a pair)
    "Pe": 1, # Close_Punctuation	a closing punctuation mark (of a pair)
    "Pi": 1, # Initial_Punctuation	an initial quotation mark
    "Pf": 1, # Final_Punctuation	a final quotation mark
    "Po": 1, # Other_Punctuation	a punctuation mark of other type
    "P":  1, # Punctuation	Pc | Pd | Ps | Pe | Pi | Pf | Po
    "Sm": 1, # Math_Symbol	a symbol of mathematical use
    "Sc": 1, # Currency_Symbol	a currency sign
    "Sk": 1, # Modifier_Symbol	a non-letterlike modifier symbol
    "So": 1, # Other_Symbol	a symbol of other type
    "S":  1, # Symbol	Sm | Sc | Sk | So
    "Zs": 0, # Space_Separator	a space character (of various non-zero widths)
    "Zl": 0, # Line_Separator	U+2028 LINE SEPARATOR only
    "Zp": 0, # Paragraph_Separator	U+2029 PARAGRAPH SEPARATOR only
    "Z":  1, # Separator	Zs | Zl | Zp
    "Cc": 0, # Control	a C0 or C1 control code
    "Cf": 0, # Format	a format control character
    "Cs": 0, # Surrogate	a surrogate code point
    "Co": 0, # Private_Use	a private-use character
    "Cn": 0, # Unassigned	a reserved unassigned code point or a noncharacter
    "C":  0, # Other	Cc | Cf | Cs | Co | Cn
}

ascii_table = dict(
    (unichr(i), chr_to_ascii(unichr(i)))
    for i in range(255)
)

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

def console(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv) != 1:
        name = argv[0]
        if name.startswith("/"):
            name = os.path.basename(name)
        print("Usage: %s" %(argv[0], ))
        print()
        print("Pipe Python literals into %s to pretty-print them" %(argv[0], ))
        return 1
    obj = ast.literal_eval(sys.stdin.read().strip())
    pprint(obj)
    return 0

def monkeypatch(mod=None, quiet=False):
    if "pprint" in sys.modules and not quiet:
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

    def write(self, data):
        if self.write_constrain is not None:
            self.write_constrain -= len(data)
            if self.write_constrain < 0:
                raise self.WriteConstrained

        if isinstance(data, BytesType):
            data = data.decode("latin1")
        self.stream.write(data)
        nl_idx = data.rfind("\n")
        if nl_idx < 0:
            self.s.cur_line_length += len(data)
        else:
            self.s.cur_line_length = len(data) - (nl_idx + 1)

    def get_indent_string(self):
        return (self.level * self.indent) * " "

def _mk_open_close_empty_dict(type_tuples):
    """ Generates a dictionary mapping either ``cls.__repr__`` xor ``cls`` to
        a tuple of ``(container_type, repr_open, repr_close, repr_empty)`` (see
        ``PrettyPrinter._open_close_empty`` for examples).

        Using either ``cls.__repr__`` xor ``cls`` is important because some
        types (specifically, ``set`` and ``frozenset`` on PyPy) share a
        ``__repr__``. When we are determining how to repr an object, the type
        is first checked, then if it's not found ``type.__repr__`` is checked.

        Note that ``__repr__`` is used so that trivial subclasses will behave
        sensibly. """

    res = {}
    for (cls, open_close_empty) in type_tuples:
        if cls.__repr__ in res:
            res[cls] = (cls, ) + open_close_empty
        else:
            res[cls.__repr__] = (cls, ) + open_close_empty
    return res

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
        sio = TextIO()
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

    _open_close_empty = _mk_open_close_empty_dict([
        (dict, ("dict", "{", "}", "{}")),
        (list, ("list", "[", "]", "[]")),
        (tuple, ("tuple", "(", ")", "()")),
        (set, ("set", "__PP_TYPE__([", "])", "__PP_TYPE__()")),
        (frozenset, ("set", "__PP_TYPE__([", "])", "__PP_TYPE__()")),
        (Counter, ("dict", "__PP_TYPE__({", "})", "__PP_TYPE__()")),
        (defaultdict, ("dict", None, "})", None)),
        (OrderedDict, ("odict", "__PP_TYPE__([", "])", "__PP_TYPE__()")),
    ])

    def _format_nested_objects(self, object, state, typeish=None):
        objid = id(object)
        state.level += 1
        state.context[objid] = 1
        try:
            # First, try to fit everything on one line. For simplicity, assume
            # that it takes three characters to close the object (ex, `]),`)
            oneline_state = state.clone(clone_shared=True)
            oneline_state.stream = TextIO()
            oneline_state.write_constrain = (
                state.max_width - state.s.cur_line_length - 3
            )
            try:
                self._write_nested_real(object, oneline_state, typeish,
                                        oneline=True)
                oneline_value = oneline_state.stream.getvalue()
                if "\n" in oneline_value:
                    oneline_value = None
            except oneline_state.WriteConstrained:
                oneline_value = None
            if oneline_value is not None:
                state.write(oneline_value)
                return
            state.write("\n" + state.get_indent_string())
            self._write_nested_real(object, state, typeish)
        finally:
            state.level -= 1
        state.write(state.get_indent_string())

    def _write_nested_real(self, object, state, typeish, oneline=False):
        indent_str = state.get_indent_string()
        first = True
        joiner = oneline and ", " or ",\n" + indent_str
        if typeish == "dict":
            for k, v in _sorted(object.items()):
                if first:
                    first = False
                else:
                    state.write(joiner)
                self._format(k, state)
                state.write(": ")
                self._format(v, state)
        elif typeish == "odict":
            for k, v in _iteritems(object):
                if first:
                    first = False
                else:
                    state.write(joiner)
                state.write("(")
                self._format(k, state)
                state.write(", ")
                self._format(v, state)
                state.write(")")
        else:
            if typeish == "set":
                object = _sorted(object)
            for o in object:
                if first:
                    first = False
                else:
                    state.write(joiner)
                self._format(o, state)
        if oneline and typeish == "tuple" and len(object) == 1:
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
        r = typ.__repr__
        # Note: see comments on _mk_open_close_empty_dict for the rational
        # behind looking up based first on type then on __repr__.
        try:
            opener_closer_empty = (
                self._open_close_empty.get(typ) or
                self._open_close_empty.get(r)
            )
        except TypeError:
            # This will happen if the type or the __repr__ is unhashable.
            # See: https://github.com/wolever/pprintpp/issues/18
            opener_closer_empty = None

        if opener_closer_empty is not None:
            orig_type, typeish, opener, closer, empty = opener_closer_empty
            if typ != orig_type:
                if opener is not None and "__PP_TYPE__" not in opener:
                    opener = "__PP_TYPE__(" + opener
                    closer = closer + ")"
                if empty is not None and "__PP_TYPE__" not in empty:
                    empty = "__PP_TYPE__(%s)" %(empty, )

            if r == defaultdict.__repr__:
                factory_repr = object.default_factory
                opener = "__PP_TYPE__(%r, {" %(factory_repr, )
                empty = opener + closer

            length = len(object)
            if length == 0:
                if "__PP_TYPE__" in empty:
                    empty = empty.replace("__PP_TYPE__", typ.__name__)
                write(empty)
                return

            if "__PP_TYPE__" in opener:
                opener = opener.replace("__PP_TYPE__", typ.__name__)
            write(opener)
            self._format_nested_objects(object, state, typeish=typeish)
            write(closer)
            return

        if r == BytesType.__repr__:
            write(repr(object))
            return

        if r == TextType.__repr__:
            if "'" in object and '"' not in object:
                quote = '"'
                quotes = {'"': '\\"'}
            else:
                quote = "'"
                quotes = {"'": "\\'"}
            qget = quotes.get
            ascii_table_get = ascii_table.get
            unicat_get = unicodedata.category
            write(u_prefix + quote)
            for char in object:
                if ord(char) > 0x7F:
                    cat = unicat_get(char)
                    if unicode_printable_categories.get(cat):
                        try:
                            write(char)
                            continue
                        except UnicodeEncodeError:
                            pass
                write(
                    qget(char) or
                    ascii_table_get(char) or
                    chr_to_ascii(char)
                )
            write(quote)
            return

        orepr = repr(object)
        orepr = orepr.replace("\n", "\n" + state.get_indent_string())
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
    try:
        import numpy as np
    except ImportError:
        class np(object):
            @staticmethod
            def array(o):
                return o

    somelist = [1,2,3]
    recursive = []
    recursive.extend([recursive, recursive, recursive])
    pprint({
        "a": {"a": "b"},
        "b": [somelist, somelist],
        "c": [
            (1, ),
            (1,2,3),
        ],
        "ordereddict": OrderedDict([
            (1, 1),
            (10, 10),
            (2, 2),
            (11, 11)
        ]),
        "counter": [
            Counter(),
            Counter("asdfasdfasdf"),
        ],
        "dd": [
            defaultdict(int, {}),
            defaultdict(int, {"foo": 42}),
        ],
        "frozenset": frozenset("abc"),
        "np": [
            "hello",
            #np.array([[1,2],[3,4]]),
            "world",
        ],
        u"u": ["a", u"\u1234", "b"],
        "recursive": recursive,
        "z": {
            "very very very long key stuff 1234": {
                "much value": "very nest! " * 10,
                u"unicode": u"4U!'\"",
            },
            "aldksfj alskfj askfjas fkjasdlkf jasdlkf ajslfjas": ["asdf"] * 10,
        },
    })
    pprint(u"\xe9e\u0301")
    uni_safe = u"\xe9 \u6f02 \u0e4f \u2661"
    uni_unsafe = u"\u200a \u0301 \n"
    unistr = uni_safe + " --- " + uni_unsafe
    sys.modules.pop("locale", None)
    pprint(unistr)
    stream = TextIO(encoding="ascii")
    pprint(unistr, stream=stream)
    print(stream.getvalue())


def load_ipython_extension(ipython):
    from .ipython import load_ipython_extension
    return load_ipython_extension(ipython)


def unload_ipython_extension(ipython):
    from .ipython import unload_ipython_extension
    return unload_ipython_extension(ipython)
