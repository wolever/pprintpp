from __future__ import print_function

import sys
from contextlib import redirect_stdout
import io
import pytest

sys.path.append("pp/")
import pp
import pprintpp as p
from pprintpp import Counter, defaultdict, OrderedDict

def test_pp():
    expected = "['hello', 'world']"
    f = io.StringIO()
    with redirect_stdout(f):
        pp(["hello", "world"])
    actual = f.getvalue().rstrip("\n")
    assert actual == expected

def test_pp_print():
    expected = "'stuff'"
    f = io.StringIO()
    with redirect_stdout(f):
        pp.pprint("stuff")
    actual = f.getvalue().rstrip("\n")
    assert actual == expected

def test_fmt():
    expected = "'asdf'\n'stuff'"
    f = io.StringIO()
    with redirect_stdout(f):
        print(pp.pformat("asdf"))
        print(pp.fmt("stuff"))
    actual = f.getvalue().rstrip("\n")
    assert actual == expected

def test_module_like():
     print(dir(pp))
     print(repr(pp))

uni_safe = "\xe9 \u6f02 \u0e4f \u2661"
uni_unsafe = "\u200a \u0302 \n"
slashed = lambda s: u"%s'%s'" %(
    p.u_prefix,
    s.encode("ascii", "backslashreplace").decode("ascii").replace("\n", "\\n")
)

@pytest.mark.skip('fix')
@pytest.mark.parametrize("input,expected,encoding", [
    (uni_safe, "%s'%s'" %(p.u_prefix, uni_safe), "utf-8"),
    (uni_unsafe, slashed(uni_unsafe), "utf-8"),
    (uni_unsafe, slashed(uni_unsafe), "ascii"),
    ("\U0002F9B2", slashed("\U0002F9B2"), "ascii")
])
def test_unicode(input, expected, encoding):
    stream = p.TextIO(encoding=encoding)
    p.pprint(input, stream=stream)
    assert stream.getvalue().rstrip("\n") == expected

test_back_and_forth_data = [
    "'\\'\"'",
    '"\'"',
    "'\"'",
    "frozenset(['a', 'b', 'c'])",
    "set([None, 1, 'a'])",
    "[]",
    "[1]",
    "{}",
    "{1: 1}",
    "set()",
    "set([1])",
    "frozenset()",
    "frozenset([1])",
    "()",
    "(1, )",
    "MyDict({})",
    "MyDict({1: 1})",
    "MyList([])",
    "MyList([1])",
    "MyTuple(())",
    "MyTuple((1, ))",
    "MySet()",
    "MySet([1])",
    "MyFrozenSet()",
    "MyFrozenSet([1])",
    "Counter()",
    "Counter({1: 1})",
    "OrderedDict()",
    "OrderedDict([(1, 1), (5, 5), (2, 2)])",
    "MyOrderedDict()",
    "MyOrderedDict([(1, 1)])",
    "MyCounter()",
    "MyCounter({1: 1})",
    "MyCounterWithRepr('dummy')",
]

class MyDict(dict):
    pass

class MyList(list):
    pass

class MyTuple(tuple):
    pass

class MySet(set):
    pass

class MyFrozenSet(frozenset):
    pass

class MyOrderedDict(p.OrderedDict):
    pass

class MyDefaultDict(p.defaultdict):
    pass

class MyCounter(p.Counter):
    pass

class MyCounterWithRepr(p.Counter):
    def __repr__(self):
        return "MyCounterWithRepr('dummy')"

@pytest.mark.skip('fix')
@pytest.mark.parametrize("expected", test_back_and_forth_data)
def test_back_and_forth(expected):
    input = eval(expected)
    stream = p.TextIO()
    p.pprint(input, stream=stream)
    assert stream.getvalue().rstrip("\n") == expected

test_expected_input_data = [
    ("defaultdict(%r, {})" %(int, ), defaultdict(int)),
    ("defaultdict(%r, {1: 1})" %(int, ), defaultdict(int, [(1, 1)])),
    ("MyDefaultDict(%r, {})" %(int, ), MyDefaultDict(int)),
    ("MyDefaultDict(%r, {1: 1})" %(int, ), MyDefaultDict(int, [(1, 1)])),
]

@pytest.mark.skip('fix')
@pytest.mark.parametrize("expected,input", test_expected_input_data)
def test_expected_input(expected, input):
    stream = p.TextIO()
    p.pprint(input, stream=stream)
    assert stream.getvalue().rstrip("\n") == expected


def test_unhashable_repr():
    # In Python 3, C extensions can define a __repr__ method which is an
    # instance of `instancemethod`, which is unhashable. It turns out to be
    # spectacularly difficult to create an `instancemethod` and attach it to
    # a type without using C... so we'll simulate it using a more explicitly
    # unhashable type.
    # See also: http://stackoverflow.com/q/40876368/71522

    class UnhashableCallable(object):
        __hash__ = None

        def __call__(self):
            return "some-repr"

    class MyCls(object):
        __repr__ = UnhashableCallable()

    obj = MyCls()
    assert p.pformat(obj) == "some-repr"



