# polyloader.py 
#
# Copyright (c) 2016 Elf M. Sternberg <elf.sternberg@gmail.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

""" Utilities for initializing extended path-hooks into the Python runtime """
__all__ = []  # Exports nothing; this module is called for its side-effects

import os
import sys

from importlib import machinery
from importlib.machinery import SOURCE_SUFFIXES as PY_SOURCE_SUFFIXES
from pkgutil import iter_importer_modules
import sys


__author__ = 'Elf M. Sternberg'
__version__ = '2016.05.29'
__contact__ = 'elf.sternberg@gmail.com'


if sys.version_info[0:2] in [(3,3), (3,4)]:
    from importlib._bootstrap import _get_supported_file_loaders
    sourcefile_recognizer = 'importlib.SourceFileLoader'

if sys.version_info[0:2] in [(3,5)]:
    from importlib._bootstrap_external import _get_supported_file_loaders
    sourcefile_recognizer = 'importlib_external.SourceFileLoader'


def _call_with_frames_removed(f, *args, **kwds):
    # Hack.  This function name and signature is hard-coded into
    # Python's import.c.  The name and signature trigger importlib to
    # remove itself from any stacktraces.  See import.c for details.
    return f(*args, **kwds)


class ExtendedSourceFileLoader(machinery.SourceFileLoader):
    """Override the get_code method.  Falls back on the SourceFileLoader
       if it's a Python file, which will generate pyc files as needed,
       or works its way into the Extended version.  This method does
       not yet address the generation of .pyc/.pyo files from source
       files for languages other than Python.
    """

    _source_handlers = []

    @classmethod
    def get_extended_suffixes(cls):
        suffixes = [] 
        for compiler, csuffx in cls._source_handlers:
            suffixes = suffixes + list(csuffx)
        return suffixes

    @classmethod
    def get_extended_suffixes_inclusive(cls):
        return PY_SOURCE_SUFFIXES + cls.get_extended_suffixes()

    # TODO: Address the generation of .pyc/.pyo files from source files.
    # See importlib/_bootstrap.py for details in SourceFileLoader of
    # how that's done.
    def get_code(self, fullname):
        source_path = self.get_filename(fullname)
        if source_path.endswith(tuple(PY_SOURCE_SUFFIXES)):
            return super(ExtendedSourceFileLoader, self).get_code(fullname)

        for compiler, suffixes in self._source_handlers:
            if source_path.endswith(suffixes):
                return _call_with_frames_removed(compiler, source_path, fullname)
        else:
            raise ImportError("Could not find compiler for %s (%s)" % (fullname, source_path))

        
# Provide a working namespace for our new FileFinder.
class ExtendedFileFinder(machinery.FileFinder):

    # Taken from inspect.py and modified to support alternate suffixes.
    @staticmethod
    def getmodulename(path):
        fname = os.path.basename(path)
        suffixes = [(-len(suffix), suffix)
                    for suffix in (machinery.all_suffixes() + 
                                   ExtendedSourceFileLoader.get_extended_suffixes())]
        suffixes.sort()  # try longest suffixes first, in case they overlap
        for neglen, suffix in suffixes:
            if fname.endswith(suffix):
                return fname[:neglen]
        return None

    # Taken from pkgutil.py and modified to support alternate suffixes.
    @staticmethod
    def iter_modules(importer, prefix=''):
        if importer.path is None or not os.path.isdir(importer.path):
            return

        yielded = {}
        try:
            filenames = os.listdir(importer.path)
        except OSError:
            # ignore unreadable directories like import does
            filenames = []
        filenames.sort()  # handle packages before same-named modules

        for fn in filenames:
            modname = ExtendedFileFinder.getmodulename(fn)
            if modname == '__init__' or modname in yielded:
                continue

            path = os.path.join(importer.path, fn)
            ispkg = False

            if not modname and os.path.isdir(path) and '.' not in fn:
                modname = fn
                try:
                    dircontents = os.listdir(path)
                except OSError:
                    # ignore unreadable directories like import does
                    dircontents = []
                for fn in dircontents:
                    subname = ExtendedFileFinder.getmodulename(fn)
                    if subname == '__init__':
                        ispkg = True
                        break
                else:
                    continue    # not a package

            if modname and '.' not in modname:
                yielded[modname] = 1
                yield prefix + modname, ispkg
        pass


# Monkeypatch both path_hooks and iter_importer_modules to make our
# modules recognizable to the module iterator functions.  This is
# probably horribly fragile, but there doesn't seem to be a more
# robust way of doing it at the moment, and these names are stable
# from python 2.7 up.

def install(compiler, suffixes):
    """ Install a compiler and suffix(es) into Python's sys.path_hooks, so
        that modules ending with thoses suffixes will be parsed into 
        python executable modules automatically.  
    """

    if sys.version[0] >= 3:
        filefinder = [(f, i) for i, f in enumerate(sys.path_hooks)
                      if repr(f).find('path_hook_for_FileFinder') != -1]
        if not filefinder:
            return
        filefinder, fpos = filefinder[0]
    
        ExtendedSourceFileLoader._source_handlers = (ExtendedSourceFileLoader._source_handlers +
                                                     [(compiler, tuple(suffixes))])
    
        supported_loaders = _get_supported_file_loaders()
        print([repr(i) for i in supported_loaders])
        sourceloader = [(l, i) for i, l in enumerate(supported_loaders)
                        if repr(l[0]).find(sourcefile_recognizer) != -1]
        if not sourceloader:
            return
    
        sourceloader, spos = sourceloader[0]
        supported_loaders[spos] = (ExtendedSourceFileLoader,
                                   ExtendedSourceFileLoader.get_extended_suffixes_inclusive())
        sys.path_hooks[fpos] = ExtendedFileFinder.path_hook(*supported_loaders)
        iter_importer_modules.register(ExtendedFileFinder, ExtendedFileFinder.iter_modules)
        if sys.path[0] != "":
            sys.path.insert(0, "")

    if sys.version[0:2] == (2, 7):
        def loader(path):
            class Loader(object):
                def __init__(self, path):
                    self.path = path
                    
                def is_package(self, fullname):
                    dirpath = "/".join(fullname.split("."))
                    for pth in sys.path:
                        pth = os.path.abspath(pth)
                        composed_path = "%s/%s/__init__.%s" % (pth, dirpath, suffix)
                        if os.path.exists(composed_path):
                            return True
                    return False

                def load_module(self, name):
                    if name in sys.modules:
                        return sys.modules[name]

                    module = compiler(fullname, path)
                    module.__file__ = path
                    sys.modules[name] = module
                    if '.' in name:
                        parent_name, child_name = name.rsplit('.', 1)
                        setattr(sys.modules[parent_name], child_name, module)
                    sys.modules[name] = module
                    return module

            return Loader()
        
        class MetaImporter(object):
            def find_module(self, fullname, path=None):
                if fullname == 'numpy' or fullname.startswith('numpy.'):
                    _mapper.PerpetrateNumpyFixes()
                if fullname in ('_hashlib', 'ctypes'):
                    raise ImportError('%s is not available in ironclad yet' % fullname)
        
                lastname = fullname.rsplit('.', 1)[-1]
                for d in (path or sys.path):
                    pyd = os.path.join(d, lastname + '.pyd')
                    if os.path.exists(pyd):
                        return loader(pyd)
        
                return None

        sys.meta_path.insert(0, MetaImporter())
        iter_importer_modules.register(MetaImporter, meta_iterate_modules)
        
    
