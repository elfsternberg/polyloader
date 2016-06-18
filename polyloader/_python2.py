import os
import os.path
import sys
import pkgutil

class PolyLoader(pkgutil.ImpLoader):

    _loader_handlers = []
    _installed = False

    def is_package(self, fullname):
        dirpath = "/".join(fullname.split("."))
        for pth in sys.path:
            pth = os.path.abspath(pth)
            for (compiler, suffix) in self._loader_handlers:
                composed_path = "%s/%s/__init__.%s" % (pth, dirpath, suffix)
                if os.path.exists(composed_path):
                    return True
        return False


    def load_module(self, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]
        
        matches = [(compiler, suffix) for (compiler, suffix) in self._loader_handlers
                   if path.endswith(suffix)]
        if matches.length == 0:
            raise ImportError("%s is not a recognized module?" % name)

        if matches.length > 1:
            raise ImportError("Multiple possible resolutions for %s: %s" % (
                name, ', '.join([suffix for (compiler, suffix) in matches])))

        compiler = matches[0]
        module = compiler(name, path)
        module.__file__ = self.filename
        module.__name__ = self.fullname

        if self.is_package(fullname):
            module.__path__ = self.path_entry
            module.__package__ = fullname
        else:
            module.__package__ = '.'.join(fullname.split('.')[:-1])

        sys.modules[fullname] = module
        return module


# Problem to be solved: pkgutil.iter_modules depends upon
# get_importer, which requires that we uses path_hooks, not meta_path.
# This is acceptable (see: https://pymotw.com/2/sys/imports.html), but
# then it depends upon the inspect get_modulename, which in turn is
# dependent upon the __builtin__.imp.get_suffixes(), which excludes
# anything other than the builtin-recognizes suffixes.  The
# arrangement, as of Python 2.7, excludes heterogenous packages from
# being locatable by pkgutil.iter_modules.
#
# iter_modules use of the simplegeneric protocol makes things even
# harder, as the order in which finders are loaded is not available at
# runtime.
#
# Possible solutions: We provide our own pkgutils, which in turn hacks
# the iter_modules; or we provide our own finder and ensure it gets
# found before the native one.

# Why the heck python 2.6 insists on calling finders "importers" is
# beyond me.  At least in calls loaders "loaders".

class PolyFinder(object):
    def __init__(self, path = None):
        self.path = path
    
    def _pl_find_on_path(self, fullname, path=None):
        subname = fullname.split(".")[-1]
        if subname != fullname and self.path is None:
            return None
        # As in the original, we ignore the 'path' argument
        path = None
        if self.path is not None:
            path = [os.path.realpath(self.path)]

        fls = ["%s/__init__.%s", "%s.%s"]
        for fp in fls:
            for (compiler, suffix) in PolyLoader._loader_handlers:
                composed_path = fp % ("%s/%s" % (pth, dirpath), suffix)
                if os.path.exists(composed_path):
                    return PolyLoader(composed_path)
        try:
            file, filename, etc = imp.find_module(subname, path)
        except ImportError:
            return None
        return ImpLoader(fullname, file, filename, etc)
            
    def find_module(self, fullname, path=None):
        path = self._pl_find_on_path(fullname)
        if path:
            return PolyLoader(path)
        return None

def _install(compiler, suffixes):

sys.meta_path.insert(0, MetaImporter())
iter_importer_modules.register(MetaImporter, meta_iterate_modules)
