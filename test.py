from __future__ import print_function

import sys
import textwrap

from nose.tools import assert_equal
from nose_parameterized import parameterized

sys.path.append("pp/")
import pp

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

if __name__ == "__main__":
    import nose
    nose.main()
