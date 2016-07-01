import polyloader
import pytest
import py_compile
import ptutils
import stat
import sys
import os
import imp
import random
import struct

class Compiler:
    def __init__(self, pt):
        self.pt = pt

    def __call__(self, source_text, filename, *extra):
        return compile("result='Success for %s: %s'" %
                       (self.pt, source_text.rstrip()), filename, "exec")

    def __repr__(self):
        return "Compiler %s" % (self.pt)

polyloader.install(Compiler("2"), ['2'])

TESTFN = '@test'

def clean_tmpfiles(path):
    if os.path.exists(path):
        os.remove(path)
    if os.path.exists(path + 'c'):
        os.remove(path + 'c')
    if os.path.exists(path + 'o'):
        os.remove(path + 'o')

def unload(name):
    try:
        del sys.modules[name]
    except KeyError:
        pass


class Test_Paths:
    path = TESTFN

    def setup_method(self, method):
        os.mkdir(self.path)
        self.syspath = sys.path[:]

    def teardown_method(self, method):
        rmtree(self.path)
        sys.path[:] = self.syspath

    # Regression test for http://bugs.python.org/issue1293.
    def test_trailing_slash(self):
        with open(os.path.join(self.path, 'test_trailing_slash.2'), 'w') as f:
            f.write("testdata = 'test_trailing_slash'")
        sys.path.append(self.path+'/')
        mod = __import__("test_trailing_slash")
        self.assertEqual(mod.testdata, 'test_trailing_slash')
        unload("test_trailing_slash")

