# Python IMPORT

What is the *exact* syntax of the python `import` command?  What does it
mean when you write:

```
import alpha.beta.gamma
from alpha import beta
from alpha.beta import gamma
from .delta import epsilon
```

In each case, python is attempting to resolve the collection of dotted
names into a *module object*.

**module object**: A resource that is or can be compiled into a
meaningful Python *module*.  This resource could a file on a filesystem,
a cell in a database, a remote web object, a stream of bytes in an
object store, some content object in a compressed archive, or anything
that can meaningfully be said described as an array of bytes.  It could
even be dynamically generated!

**module**: The organizational unit of Python code.  A namespace
containing Python objects, including classes, functions, submodules, and
immediately invoked code.  Modules themselves may be collected into
*packages*.

**package**: A python module which contains submodules or even
subpackages.  The most common packaging scheme is a directory folder; in
this case the folder is a module if it contains an `__init__.py` file,
and it is a *package* if it contains other modules.  The name of the
package is the folder name; the name of a submodule would be
`foldername.submodule`.  This is called *regular packaging*.  An
alternative method is known as *namespace packaging*.

Python has a baroque but generally flexible mechanism for defining how
the dotted name is turned into a *module object*, which it calls *module
finding*, and for how that *module object* is turned into a *code
object* within the current Python session, called *module loading*.

Python also has a means for *listing* modules.  *Listing* is usually
done on a list of paths, using an appropriate means for accessing the
contents at the end of a path.

The technical definition of a *package* is a module with a `__path__`, a
list of paths that contain submodules for the package.  Subpackages get
their own` __path__`.  A package can therefore accomodate `.` and `..`
prefixes in submodules, indicating relative paths to sibling modules.  A
package can also and to its own `__path__` collection to enable access
to submodules elsewhere.

# Clarifying terminology

The language used for describing the import mechanism is confusing,
often horribly so.  Let's go with some clarification first.

When the 'import <fullname>' command is called, a procedure is
triggered.  That procedure then:

* attempts to *find* a corresponding python *module*
* attempts to *load* that corresponding module into *bytecode*
* Associates the bytecode with the name via sys.modules[fullname]
* Exposes the bytecode to the calling scope.

Only the first three matter for our purposes.

## FINDING

*Finding* is the act of identifying a resource that corresponds to the
import string and can be compiled into a meaningful Python module.  The
import string is typically called the *fullname*.

*Finding* typically involves scanning a collection of *resources*
against a collection of *finders*.  *Finding* ends when *finder `A`*,
given *fullname `B`*, reports that a corresponding module can be found
in *resource `C`*, and that the resource can be loaded with *loader
`D`*."

### METAFINDERS

*Finders* come first, and *MetaFinders* come before all other kinds of
finders.

_Most finding is done in the context of `sys.path`_; that is, Python's
primary means of organizing Python modules is to have them somewhere on
the local filesystem, which makes sense.  Sometimes, however, you want
to get in front of that scan.  That's what you do with a MetaFinder: A
MetaFinder may have its own take on what to do with `sys.path`; it may
choose to ignore `sys.path` entirely and do something with the import
*fullname* that has nothing to do with the local filesystem.

A Finder is any object with the following function:
    [Loader|None] find_module([self|cls], fullname:string, path:[string|None])

If find_module returns None if it cannot find a loader resource for
fullname & path.

A MetaFinder is placed into the list `sys.meta_path` by whatever code
needs the MetaFinder, and it persists for the duration of the runtime,
unless it is later removed or replaced.  Being a list, the search is
ordered; first match wins.  MetaFinders may be instantiated in any way
the developer desires before being added into `sys.meta_path`.

### PATH_HOOK

*PathHooks* are how `sys.path` is scanned to determine the which Finder
should be associated with a given directory path.

A *PathHook* is a function:
    [Finder|None] <anonymous function>(path:string)

A *PathHook* is a function that takes a given directory path and, if the
PathHook can identify a corresponding Finder for the modules in that
directory path, returns the Finder, otherwise it returns None.

If no `sys.meta_path` finder returns a loader, the full array of
`sys.paths ⨯ sys.path_hooks` is compared until a PathHook says it can
handle the path and the corresponding finder says it can handle the
fullname.  If no match happens, Python's default import behavior is
triggered.

PathHooks are placed into the list `sys.path_hooks`; like
`sys.meta_path`, the list is ordered and first one wins.

### LOADER

*Loaders* are returned by *Finders*, and are constructed by Finders with
whatever resources the developer specifies the Finder has and can
provide.  The Loader is responsible for pulling the content of the
*module object* into Python's memory and processing it into a *module*,
whether by calling Python's `eval()/compile()` functions on standard
Python code, or by some other means.



a collection of *finders* the *fullname* (the dot-separated string passed to the `import`
function).



to find a
corresponding python module, which is then compiled into Python bytecode
and incorporated into the python runtime, where it will be accessible to
the importing function or modules

MetaFinder: A python object with a single method:

    (Loader|None) find_module(self, fullname:string, path:(string|None))





Python 2.7

iter_modules (iter_importers) ->
  calls iter_importer_modules for each importer in iter_importers

iter_importers (meta_path, get_importer) ->
  returns every importer in sys.meta_path + map(get_importer, sys.path)

get_importer(path):

    returns a filtered list of sys.path_hooks for importers that can
    handle this path; if there is no match, returns ImpImporter(),
    which supplies a module iterator (ImpImporter.iter_modules) that
    relies on getmodulename.  
    
    * A path_hook is a function of (path -> Maybe importer)

iter_modules(path, get_importer, prefix) ->
  calls iter_importer_modules for each importer returned by path.map(get_importer)

iter_importer_modules(importer) ->
  returns list of (filename, ispkg) for each module understood by the importer
  * The method called depends on the class of the importer
  * The default is a generic call for "no specific importer"
  * For FILES, iter_import_modules returns a list of files whose
    extensions match those in imp.get_suffixes(), which is hard-
    coded into the interpreter.
  * MEANING: Unless your importer can handle heterogenous module
    suffixes, SourceFiles.iter_importer_modules can only find
    homogeonous modules.

This relationship issue holds for Python 2.6 as well.

Python 3.3

    The same issue holds, although now most of the extensions have been
    moved to importlib._bootstrap.

It is the relationship between
   importlib.machinery.FileFinder
and
    _iter_file_finder_modules

That's killing us.
   


---  
    
So the ONLY thing I have to do, according to Python, is assert that
there's a dir/__init__.suff and attempt to load it!  If I do that, I can
make it work?

No: The search for __init__.suff is only the first 


---

test_import: test_with_extension "py" and "my"
test_execute_bit_not_set (on Posix system, .pyc files got their
executable bit set if the .py file had it set; it looks as if Python
just copied the permissions, if it had permission to do so.  We should
follow the example of 2.7 & 3.4, and NOT set +x if we can help it).

test_rewrite_pyc_with_read_only_source (on Posix systems, if the .py
file had read-only set, the .pyc file would too, making updates
problematic).

test_import_name_binding

test_bug7732 (attempt to import a '.my' file that's not a file)



These are more Hy-related:

test_module_with_large_stack (see python example)

test_failing_import_sticks

test_failing_reload


