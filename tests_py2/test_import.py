import polyloader
import pytest
import py_compile
from . import ptutils
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

if sys.version_info[0:2] >= (2, 6):
    VERSION = 2

if sys.version_info[0] >= 3:
    VERSION = 3


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

# This exists mostly to test that the inclusion of PolyLoader doesn't
# break anything else in Python.

# Tests commented out: 2
    
class Test_Imports(object):

    def test_case_sensitivity(self):
        # Brief digression to test that import is case-sensitive:  if we got
        # this far, we know for sure that "random" exists.
        try:
            import RAnDoM
        except ImportError:
            pass
        else:
            assert(False)

    @pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                        reason="PyPy won't load bytecode if source not present.")
    def test_import(self):
        sys.path.insert(0, os.curdir)
        ext = 'py'
        try:
            # The extension is normally ".py", perhaps ".pyw".
            source = TESTFN + os.extsep + ext
            pyc = TESTFN + os.extsep + "pyc"

            with open(source, "w") as f:
                a = random.randrange(1000)
                b = random.randrange(1000)
                f.write("# This tests Python's ability to import a" + ext + "file.\n")
                f.write("a =" + str(a) + "\n")
                f.write("b =" + str(b) + "\n")
            try:
                mod = __import__(TESTFN)
            except ImportError as err:
                print("import from %s (%s) failed: %s" % (ext, os.curdir, err))
                assert(False)
            else:
                assert(mod.a == a)
                assert(mod.b == b)
            finally:
                os.remove(source)

            try:
                if not sys.dont_write_bytecode:
                    imp.reload(mod)
            except ImportError as err:
                print("import from .pyc/.pyo failed: %s" % err)
                assert(False)
            finally:
                clean_tmpfiles(source)
                unload(TESTFN)
        finally:
            del sys.path[0]

    def test_execute_bit_not_copied(self):
        # Issue 6070: under posix .pyc files got their execute bit set if
        # the .py file had the execute bit set, but they aren't executable.
        oldmask = os.umask(0o22)
        sys.path.insert(0, os.curdir)
        try:
            fname = TESTFN + os.extsep + "py"
            f = open(fname, 'w').close()
            os.chmod(fname, (stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH |
                             stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
            __import__(TESTFN)
            fn = fname + 'c'
            if not os.path.exists(fn):
                fn = fname + 'o'
                if not os.path.exists(fn):
                    self.fail("__import__ did not result in creation of "
                              "either a .pyc or .pyo file")
            s = os.stat(fn)
            assert(s.st_mode & (stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH))
            assert(not (s.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)))
        finally:
            os.umask(oldmask)
            clean_tmpfiles(fname)
            unload(TESTFN)
            del sys.path[0]

    def test_imp_module(self):
        # Verify that the imp module can correctly load and find .py files

        # XXX (ncoghlan): It would be nice to use test_support.CleanImport
        # here, but that breaks because the os module registers some
        # handlers in copy_reg on import. Since CleanImport doesn't
        # revert that registration, the module is left in a broken
        # state after reversion. Reinitialising the module contents
        # and just reverting os.environ to its previous state is an OK
        # workaround
        orig_path = os.path
        orig_getenv = os.getenv
        with ptutils.EnvironmentVarGuard():
            x = imp.find_module("os")
            new_os = imp.load_module("os", *x)
            assert(os == new_os)
            assert(orig_path == new_os.path)
            assert(orig_getenv != new_os.getenv)


    def test_failing_import_sticks(self):
        source = TESTFN + os.extsep + "py"
        with open(source, "w") as f:
            f.write("a = 1 // 0\n")

        # New in 2.4, we shouldn't be able to import that no matter how often
        # we try.
        sys.path.insert(0, os.curdir)
        try:
            for i in [1, 2, 3]:
                with pytest.raises(ZeroDivisionError) as zde:
                    __import__(TESTFN)
            assert(sys.modules.get(TESTFN) == None)
        finally:
            del sys.path[0]
            clean_tmpfiles(source)

#    def test_failing_reload(self):
#        # A failing reload should leave the module object in sys.modules.
#        source = TESTFN + os.extsep + "py"
#        with open(source, "w") as f:
#            print >> f, "a = 1"
#            print >> f, "b = 2"
#
#        sys.path.insert(0, os.curdir)
#        try:
#            mod = __import__(TESTFN)
#            assert(sys.modules.get(TESTFN) != None)
#            assert(mod.a == 1)
#            assert(mod.b == 2)
#
#            # On WinXP, just replacing the .py file wasn't enough to
#            # convince reload() to reparse it.  Maybe the timestamp didn't
#            # move enough.  We force it to get reparsed by removing the
#            # compiled file too.
#            clean_tmpfiles(TESTFN)
#
#            # Now damage the module.
#            with open(source, "w") as f:
#                print >> f, "a = 10"
#                print >> f, "b = 20 // 0"
#
#            with pytest.raises(ZeroDivisionError) as zde:
#                imp.reload(mod)
#
#            # But we still expect the module to be in sys.modules.
#            mod = sys.modules.get(TESTFN)
#            assert(mod != None)
#
#            # We should have replaced a w/ 10, but the old b value should
#            # stick.
#            assert(mod.a == 10)
#            assert(mod.b == 2)
#
#        finally:
#            del sys.path[0]
#            clean_tmpfiles(source)
#            unload(TESTFN)

    def test_infinite_reload(self):
        # http://bugs.python.org/issue742342 reports that Python segfaults
        # (infinite recursion in C) when faced with self-recursive reload()ing.

        sys.path.insert(0, os.path.dirname(__file__))
        try:
            with pytest.raises(ImportError):
                import infinite_reload
        finally:
            del sys.path[0]

    def test_import_name_binding(self):
        # import x.y.z binds x in the current namespace.
        import test as x
        import test.test_support
        assert(x == test)
        assert(hasattr(test.test_support, "__file__"))

        # import x.y.z as w binds z as w.
        import test.test_support as y
        assert(y == test.test_support)

    def test_import_initless_directory_warning(self):
        with pytest.raises(ImportError) as ie:
            __import__('site-packages')

    def test_import_by_filename(self):
        path = os.path.abspath(TESTFN)
        with pytest.raises(ImportError) as c:
            __import__(path)
        assert("Import by filename is not supported." == c.value[0])

#    def test_bug7732(self):
#        source = TESTFN + '.2'
#        os.mkdir(source)
#        try:
#            with pytest.raises(IOError) as iie:
#                mod = imp.find_module(TESTFN, ["."])
#                print("Found mod %s" % mod)
#        finally:
#            os.rmdir(source)

