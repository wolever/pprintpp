from __future__ import print_function

import sys
import ctypes
import textwrap

from nose.tools import assert_equal
from nose_parameterized import parameterized, param

sys.path.append("pp/")
import pp
import pprintpp as p
from pprintpp import Counter, defaultdict, OrderedDict

class PPrintppTestBase(object):
    def assertStdout(self, expected, trim=True):
        if trim:
            expected = textwrap.dedent(expected.rstrip().lstrip("\n"))
        # Assumes that nose's capture plugin is active
        assert_equal(sys.stdout.getvalue().rstrip(), expected)


class TestPP(PPrintppTestBase):
    def test_pp(self):
        pp(["hello", "world"])
        self.assertStdout("['hello', 'world']")

    def test_pp_pprint(self):
        pp.pprint("stuff")
        self.assertStdout("'stuff'")

    def test_fmt(self):
        print(pp.pformat("asdf"))
        print(pp.fmt("stuff"))
        self.assertStdout("""
            'asdf'
            'stuff'
        """)

    def test_module_like(self):
        print(dir(pp))
        print(repr(pp))


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

class TestPPrint(PPrintppTestBase):
    uni_safe = u"\xe9 \u6f02 \u0e4f \u2661"
    uni_unsafe = u"\u200a \u0302 \n"
    slashed = lambda s: u"%s'%s'" %(
        p.u_prefix,
        s.encode("ascii", "backslashreplace").decode("ascii").replace("\n", "\\n")
    )

    @parameterized([
        param("safe", uni_safe, "%s'%s'" %(p.u_prefix, uni_safe)),
        param("unsafe", uni_unsafe, slashed(uni_unsafe)),
        param("encoding-aware", uni_safe, slashed(uni_safe), encoding="ascii"),
        param("high-end-chars", u"\U0002F9B2", slashed(u"\U0002F9B2"), encoding="ascii"),
    ])
    def test_unicode(self, name, input, expected, encoding="utf-8"):
        stream = p.TextIO(encoding=encoding)
        p.pprint(input, stream=stream)
        assert_equal(stream.getvalue().rstrip("\n"), expected)

    @parameterized([
        param(u"'\\'\"'"),
        param(u'"\'"'),
        param(u"'\"'"),
        param("frozenset(['a', 'b', 'c'])"),
        param("set([None, 1, 'a'])"),

        param("[]"),
        param("[1]"),
        param("{}"),
        param("{1: 1}"),
        param("set()"),
        param("set([1])"),
        param("frozenset()"),
        param("frozenset([1])"),
        param("()"),
        param("(1, )"),

        param("MyDict({})"),
        param("MyDict({1: 1})"),
        param("MyList([])"),
        param("MyList([1])"),
        param("MyTuple(())"),
        param("MyTuple((1, ))"),
        param("MySet()"),
        param("MySet([1])"),
        param("MyFrozenSet()"),
        param("MyFrozenSet([1])"),

    ] + ([] if not p._test_has_collections else [
        param("Counter()"),
        param("Counter({1: 1})"),
        param("OrderedDict()"),
        param("OrderedDict([(1, 1), (5, 5), (2, 2)])"),
        param("MyOrderedDict()"),
        param("MyOrderedDict([(1, 1)])"),
        param("MyCounter()"),
        param("MyCounter({1: 1})"),
        param("MyCounterWithRepr('dummy')"),
    ]))
    def test_back_and_forth(self, expected):
        input = eval(expected)
        stream = p.TextIO()
        p.pprint(input, stream=stream)
        assert_equal(stream.getvalue().rstrip("\n"), expected)

    if p._test_has_collections:
        @parameterized([
            param("defaultdict(%r, {})" %(int, ), defaultdict(int)),
            param("defaultdict(%r, {1: 1})" %(int, ), defaultdict(int, [(1, 1)])),
            param("MyDefaultDict(%r, {})" %(int, ), MyDefaultDict(int)),
            param("MyDefaultDict(%r, {1: 1})" %(int, ), MyDefaultDict(int, [(1, 1)])),
        ])
        def test_expected_input(self, expected, input):
            stream = p.TextIO()
            p.pprint(input, stream=stream)
            assert_equal(stream.getvalue().rstrip("\n"), expected)

    def test_unhashable_repr(self):
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
        assert_equal(p.pformat(obj), "some-repr")


if __name__ == "__main__":
    import nose
    nose.main()
