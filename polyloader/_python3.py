import os
import sys

from importlib import machinery
from importlib.machinery import SOURCE_SUFFIXES as PY_SOURCE_SUFFIXES
from pkgutil import iter_importer_modules
import sys


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


class PolySourceFileLoader(machinery.SourceFileLoader):
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
class PolySourceFileFinder(machinery.FileFinder):

    


    

    
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

    
        

def install(compiler, suffixes):
    """Install a specialized version of FileFinder that will search
       through alternative extensions first for syntax files and, upon
       encountering one, will return a specialized version of
       SourceFileLoader for that syntax.  By replacing this into
       path_hook this makes both import and iter_modules work as
       expected.
    """
    
    
    filefinder = [(f, i) for i, f in enumerate(sys.path_hooks)
                  if repr(f).find('.path_hook_for_FileFinder') != -1]
    if not filefinder:
        return
    filefinder, fpos = filefinder[0]
    
    
    
    
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



class PolySourceFileLoader(FileLoader):
    
        

class PolyFileFinder(FileFinder):
    '''The poly version of FileFinder supports the addition of loaders
       after initialization.  That's pretty much the whole point of the 
       PolyLoader mechanism.'''

    _native_loaders = []
    _custom_loaders = []
    _installed = False
    
    def __init__(self, path):
        # Base (directory) path
        self.path = path or '.'
        self._path_mtime = -1
        self._path_cache = set()
        self._relaxed_path_cache = set()

    @property
    def _loaders(self):
        return cls._native_loaders + cls._custom_loaders
        
    @classmethod
    def path_hook(cls):
        if not _path_isdir(path):
            # By now, we've exhausted every loader except this one, so...
            raise ImportError("only directories are supported", path=path)
        return cls(path)

def install(compiler, suffixes):
    if not PolyFileFinder._installed:
        PolyFileFinder._native_loaders = machinery._get_supported_file_loaders()
        filefinder = [(f, i) for i, f in enumerate(sys.path_hooks)
                      if repr(f).find('.path_hook_for_FileFinder') != -1]
        if filefinder:
            filefinder, fpos = filefinder[0]
            sys.path_hooks[fpos] = PolyFileFinder.path_hook
        else:
            sys.path_hooks.extend([PolyFileFinder.path_hook])
        PolyFileFinder._installed = True
    PolyFileFinder._install(compiler, suffixes)
