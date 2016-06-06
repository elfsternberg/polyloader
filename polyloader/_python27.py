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

                
class PolyFinder(pkgutil.ImpImporter):
    def find_on_path(self, fullname):
        fls = ["%s/__init__.%s", "%s.%s"]
        dirpath = "/".join(fullname.split("."))

        for pth in sys.path:
            pth = os.path.abspath(pth)
            for fp in fls:
                for (compiler, suffix) in PolyLoader._loader_handlers:
                    composed_path = fp % ("%s/%s" % (pth, dirpath), suffix)
                    if os.path.exists(composed_path):
                        return composed_path

    def find_module(self, fullname, path=None):
        path = self.find_on_path(fullname)
        if path:
            return PolyLoader(path)


def _install(compiler, suffixes):
                              
                

sys.meta_path.insert(0, MetaImporter())
iter_importer_modules.register(MetaImporter, meta_iterate_modules)
