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


class Test_RelativeImports:

    def teardown_class(cls):
        unload("tests.relimport")

    def setup_class(cls):
        unload("tests.relimport")

    def test_relimport_star(self):
        # This will import * from .test_import.
        from . import relimport
        assert(hasattr(relimport, "Test_Imports"))

    def test_issue3221(self):
        # Regression test for http://bugs.python.org/issue3221.
        def check_absolute():
            exec "from os import path" in ns
        def check_relative():
            exec "from . import relimport" in ns

        # Check both OK with __package__ and __name__ correct
        ns = dict(__package__='tests', __name__='test.notarealmodule')
        check_absolute()
        check_relative()

        # Check both OK with only __name__ wrong
        ns = dict(__package__='tests', __name__='notarealpkg.notarealmodule')
        check_absolute()
        check_relative()

        # Check relative fails with only __package__ wrong
        ns = dict(__package__='foo', __name__='test.notarealmodule')
        with pytest.warns(RuntimeWarning) as rw:
            check_absolute()
        with pytest.raises(SystemError) as se:
            check_relative()

        # Check relative fails with __package__ and __name__ wrong
        ns = dict(__package__='foo', __name__='notarealpkg.notarealmodule')
        with pytest.warns(RuntimeWarning) as se:
            check_absolute()
        with pytest.raises(SystemError) as se:
            check_relative()

        # Check both fail with package set to a non-string
        ns = dict(__package__=object())
        with pytest.raises(ValueError) as ve:
            check_absolute()
        with pytest.raises(ValueError) as ve:
            check_relative()

    def test_absolute_import_without_future(self):
        # If explicit relative import syntax is used, then do not try
        # to perform an absolute import in the face of failure.
        # Issue #7902.
        with pytest.raises(ImportError) as ie:
            from .os import sep
            assert(False)
