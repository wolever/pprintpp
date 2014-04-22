from __future__ import print_function

import sys
import textwrap

from nose.tools import assert_equal
from nose_parameterized import parameterized, param

sys.path.append("pp/")
import pp
import pprintpp as p

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


class TestPPrint(PPrintppTestBase):
    uni_safe = u"\xe9 \u6f02 \u0e4f \u2661"
    uni_unsafe = u"\u200a \u0301"
    slashed = lambda s: repr(s)

    @parameterized([
        param("safe", uni_safe, "%s'%s'" %(p.u_prefix, uni_safe)),
        param("unsafe", uni_unsafe, slashed(uni_unsafe)),
        param("encoding-aware", uni_safe, slashed(uni_safe), encoding="ascii"),
    ])
    def test_unicode(self, _, input, expected, encoding="utf-8"):
        stream = p.TextIO(encoding=encoding)
        p.pprint(input, stream=stream)
        assert_equal(stream.getvalue().rstrip("\n"), expected)


if __name__ == "__main__":
    import nose
    nose.main()
