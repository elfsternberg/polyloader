#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_polyloader
----------------------------------

Tests for `polyloader` module.
"""

import pytest

from polyloader import polyloader

# Note that these compilers don't actually load much out of the
# source files.  That's not the point.  The point is to show that the
# correct compiler has been found for a given extension.

def compiler(pt):
    def _compiler(source_path, modulename):
        with open(source_path, "r") as file:
            return compile("result='Success for %s: %s'" % (pt, file.readline().rstrip()), modulename, "exec")
    return _compiler

class Test_Polymorph_1(object):
    def test_import1(self):
        polyloader.install(compiler("2"), ['.2'])
        polyloader.install(compiler("3"), ['.3'])
        from .polytestmix import test2
        from .polytestmix import test3
        assert(test2.result == "Success for 2: Test Two")
        assert(test3.result == "Success for 3: Test Three")

class Test_Polymorph_Iterator(object):
    ''' The Django Compatibility test: Can we load arbitrary modules from a package? '''
    def test_iterator(self):
        import os
        import pkgutil
        import inspect
        polyloader.install(compiler("2"), ['.2'])
        polyloader.install(compiler("3"), ['.3'])
        from .polytestmix import test2
        from .polytestmix import test3
        target_dir = os.path.join(
            os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),
            'polytestmix')
        modules = set([name for _, name, is_pkg in pkgutil.iter_modules([target_dir])
            if not is_pkg and not name.startswith('_')])
        assert(modules == set(['test1', 'test2', 'test3']))
                    
        

