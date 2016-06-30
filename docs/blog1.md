A minor bug in the Hy programming language has led me down a rabbit hole
of Python's internals, and I seem to have absorbed an awful lot of
Python's
[`import`](https://docs.python.org/2.7/reference/simple_stmts.html#import)
semantics.  The main problem can best be described this way: In Python,
you call the import function with a string; that string gets translated
in some way into python code.  So: what are the *exact* semantics of the
python `import` command?

Over the next couple of posts, I'll try to accurately describe what it
means when you write:

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
that can meaningfully be described as an array of bytes (Python 2) or
characters (Python 3).  It could even be dynamically generated!

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
alternative method, which we will address later, is known as *namespace
packaging*.

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

--

The problem I am trying to solve:

Python *module listing* depends upon *finder* resolving a *path* to to a
container of modules, usually (but not necessarily) a *package*.  The
very last finder is the default one: after all alternatives provided by
users have been exhausted, Python reverts to the default behavior of
analyzing the filesystem, as one would expect.  The default finder is
hard-coded to use the Python builtin `imp.get_suffixes()` function,
which in turn hard-codes the extensions recognized by the importer.

If one wants to supply alternative syntaxes for Python and have
heterogenous packages (for examples, packages that contain some modules
ending in `.hy`, and others `.py`, side-by-side)... well, that's just
not possible.

Yet.

In the next post, I'll discuss Python's two different *finder*
resolution mechanisms, the *meta_path* and the *path_hook*, and how they
differ, and which one we'll need to instantiate to solve the problem of
heterogenous Python syntaxes.  The actual solution will eventually
involve *eclipsing* Python's default source file handler with one that
enables us to define new source file extensions at run-time, recognize
the source file extensions, and supply the appropriate compilers for
them.

My hope is that, once solved, this will further enable the development
of Python alternative syntaxes.  Folks bemoan the
[explosion of Javascript precompilers](https://github.com/jashkenas/coffeescript/wiki/list-of-languages-that-compile-to-js),
but the truth is that it has in part led to a revival in industrial
programming languages and a renaissance in programming language
development in general.
