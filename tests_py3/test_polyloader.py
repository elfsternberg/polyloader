#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_polyloader
----------------------------------

Tests for `polyloader` module.
"""

import polyloader
import copy
import sys

# Note that these compilers don't actually load much out of the
# source files.  That's not the point.  The point is to show that the
# correct compiler has been found for a given extension.


class ImportEnvironment(object):
    def __init__(self):
        pass
    
    def __enter__(self):
        polyloader.reset()
        self.path = copy.copy(sys.path)
        self.path_hooks = copy.copy(sys.path_hooks)
        self.meta_path = copy.copy(sys.meta_path)
        self.modules = copy.copy(sys.modules)
        self.path_importer_cache = copy.copy(sys.path_importer_cache)
        return sys

    def __exit__(self, type, value, traceback):
        sys.path = self.path
        sys.path_hooks = self.path_hooks
        sys.meta_path = self.meta_path
        sys.modules = self.modules
        sys.path_importer_cache = self.path_importer_cache


class Compiler:
    def __init__(self, pt):
        self.pt = pt

    def __call__(self, source_text, filename, *extra):
        return compile("result='Success for %s: %s'" %
                       (self.pt, source_text.rstrip()), filename, "exec")

    def __repr__(self):
        return "Compiler %s" % (self.pt)
        
def compiler(pt):
    return Compiler(pt)

# Functionally, the "From" test and the "Direct" test should be
# indistinguishable.  What's interesting about them, though, is that
# in the context of the caller, the "Direct" test now has test and
# test.polytestmix as objects in the calling context.  They're fairly
# lightweight, but they do exist, and they do honor the __all__ and
# __path__ cases.
#
# Also:
# See http://python-notes.curiousefficiency.org/en/latest/python_concepts/import_traps.html
# for some 'gotchas' to look forward to.  Whee.

class Test_Polymorph_From(object):
    def test_import1(self):
        with ImportEnvironment() as sys:
            polyloader.install(compiler("2"), ['2'])
            polyloader.install(compiler("3"), ['3'])
            from .polytestmix import test2
            from .polytestmix import test3
            from .polytestmix import test1
            assert(test1.result == "Success for 1: Test One")
            assert(test2.result == "Success for 2: Test Two")
            assert(test3.result == "Success for 3: Test Three")

class Test_Polymorph_Direct(object):
    def test_import2(self):
        with ImportEnvironment() as sys:
            polyloader.install(compiler("2"), ['2'])
            polyloader.install(compiler("3"), ['3'])
            import tests_py2.polytestmix.test2
            import tests_py2.polytestmix.test3
            import tests_py2.polytestmix.test1
            assert(tests_py2.polytestmix.test1.result == "Success for 1: Test One")
            assert(tests_py2.polytestmix.test2.result == "Success for 2: Test Two")
            assert(tests_py2.polytestmix.test3.result == "Success for 3: Test Three")

class Test_Polymorph_Module(object):
    def test_import3(self):
        with ImportEnvironment() as sys:
            polyloader.install(compiler("3"), ['3'])
            polyloader.install(compiler("2"), ['2'])
            from tests_py2.polytestmix.test3 import result as result3
            from tests_py2.polytestmix.test2 import result as result2
            from tests_py2.polytestmix.test1 import result as result1
            assert(result1 == "Success for 1: Test One")
            assert(result2 == "Success for 2: Test Two")
            assert(result3 == "Success for 3: Test Three")

class Test_Polymorph_Iterator(object):
    ''' The Django Compatibility test: Can we load arbitrary modules from a package? '''
    def test_iterator(self):
        with ImportEnvironment() as sys:
            import os
            import inspect
            polyloader.install(compiler("2"), ['.2'])
            polyloader.install(compiler("3"), ['.3'])
            import pkgutil
            target_dir = os.path.join(
                os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),
                'polytestmix')
            modules = set([name for (_, name, is_pkg) in pkgutil.iter_modules([target_dir])
                           if not is_pkg and not name.startswith('_')])
            assert(modules == set(['test1', 'test2', 'test3']))

