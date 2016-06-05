#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_py-polymorphic-loader
----------------------------------

Tests for `py-polymorphic-loader` module.
"""

import pytest


from py_polymorphic_loader import polymorph

# Note that these compilers don't actually load anything out of the
# source files.  That's not the point.  The point is to show that the
# correct compiler has been found for a given extension.

def compiler2(filename):
    return compile("result='Success for %s'" % (filename), filename, "exec")

def compiler3(filename):
    return compile("result='Success for %s'" % (filename), filename, "exec")

class Test_Polymorph_1(object):
    def test_import1(self):
        import polytestmix
        polytestmix.install(compiler2, ['.2'])
        polytestmix.install(compiler3, ['.3'])
        assert(polytestmix.test2.result = "Success for test2")
        assert(polytestmix.test3.result = "Success for test3")

class Test_Polymorph_2(object):
    def test_import2(self):
        import polytestmix
        polytestmix.install(compiler2, ['.2'])
        polytestmix.install(compiler3, ['.3'])
        assert(polytestmix.test2.result = "Success for test2")

class Test_Polymorph_2(object):
    def test_import2(self):
        import polytestmix.test3
        polytestmix.install(compiler2, ['.2'])
        polytestmix.install(compiler3, ['.3'])
        assert(polytestmix.test3.result = "Success for test3")

class Test_Polymorph_Iterator(object):
    ''' The Django Compatibility test. '''
    def test_iterator(self):
        import polytestmix.test3
        polytestmix.install(compiler2, ['.2'])
        polytestmix.install(compiler3, ['.3'])
        target_dir = os.path.join('.', 'polytestmix')
        files = set([name for _, name, is_pkg in pkgutil.iter_modules([targetdir])
            if not is_pkg and not name.startswith('_')])
        assert(files == set(['test2.2', 'test3.3', 'test1.py']))
                    
        
