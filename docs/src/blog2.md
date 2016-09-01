In the last post, I introduced the concepts of the **module object**,
**module**, and **package**, concrete objects that exist within the
Python runtime, as well as some basic ideas about packaging, finding,
and loading.

In this post, I'll go over the process of *finding*, what it means to
*find* something, and what happens next.

## A Clarifying point

I've been very careful to talk about *finding* vs. *loading*
vs. *listing* in this series of posts.  There's a reason for that: in
Python 2, the terms "Finder" and "Importer" were used interchangeably,
leading to (at least on my part) massive confusion.  In actual fact,
finders, hooks, loaders, and listers are all individual objects, each
with a single, unique method with a specific signature.  The method name
is different for each stage, so it is theoretically possible to define a
single class that does all three for a given category of *module
object*, and only in that case, I believe, should we talk about an
"Importer."

In Python 2.6 and 2.7, the definitive Finder class is called
`pkgutil.ImpImporter`, and the Loader is called `pkgutil.ImpLoader`;
this was a source of much of my confusion.  In Python 3, the term
"Importer" is deprecated and "Finder" is used throughout `importlib`.  I
will be using "Finder" from now on.

## Finding

When the 'import <fullname>' command is called, a procedure is
triggered.  That procedure then:

* attempts to *find* a corresponding python *module*
* attempts to *load* that corresponding module into *bytecode*
* Associates the bytecode with the name via sys.modules[fullname]
* Exposes the bytecode to the calling scope.
* Optionally: writes the bytecode to the filesystem for future use

*Finding* is the act of identifying a resource that corresponds to the
import string that can be compiled into a meaningful Python module.  The
import string is typically called the *fullname*.

*Finding* typically involves scanning a collection of *resources*
against a collection of *finders*.  *Finding* ends when *finder `A`*,
given *fullname `B`*, reports that a corresponding module can be found
in *resource `C`*, and that the resource can be loaded with *loader
`D`*."

### MetaFinders

*Finders* come first, and *MetaFinders* come before all other kinds of
finders.

_Most finding is done in the context of `sys.path`_; that is, Python's
primary means of organizing Python modules is to have them somewhere on
the local filesystem.  This makes sense.  Sometimes, however, you want
to get in front of that scan and impose your own logic: you want the
root of an import string to mean something else.  Maybe instead of
`directory.file`, you want it to mean `table.row.cell`, or you want it
to mean `website.path,object`, to take
[one terrifying example](http://blog.dowski.com/2008/07/31/customizing-the-python-import-system/).

That's what you do with a MetaFinder: A MetaFinder may choose to ignore
the entire sys.path mechanism and do something that has nothing to do
with the filesystem, or it may have its own take on what to do with
`sys.path`.

A Finder is any object with the following method:
```
[Loader|None] find_module([self|cls], fullname:string, path:[string|None])
```

The find_module method returns None if it cannot find a loader resource
for fullname & path.

A MetaFinder is placed into the list `sys.meta_path` by whatever code
needs the MetaFinder, and it persists for the duration of the runtime,
unless it is later removed or replaced.  Being a list, the search is
ordered; first match wins.  MetaFinders may be instantiated in any way
the developer desires before being added into `sys.meta_path`.

### PathHooks and PathFinders

*PathHooks* are how `sys.path` is scanned to determine the which Finder
should be associated with a given directory path.

A PathHook is a function (or callable):
```
[Finder|None] <anonymous function>(path:string)
```

A *PathHook* takes a given directory path and, if the PathHook can
identify a corresponding FileFinder for the modules in that directory
path and return a constructed instance of that FileFinder, otherwise it
returns None.

If no `sys.meta_path` finder returns a loader, the full array of
`sys.paths ⨯ sys.path_hooks` is compared until a PathHook says it can
handle the path _and_ the corresponding finder says it can handle the
fullname.  If no match happens, Python's default FileFinder class is
instantiated with the path.

This means that for each path in `sys.paths`, the list of
`sys.path_hooks` is scanned; the first function to return an importer is
handed responsibility for that path; if no function returns, the default
FileFinder is returned; the default FileFinder returns only the default
SourceFileLoader which (if you read to the end of
[part one](http://elfsternberg.com)) blocks our path toward
heterogeneous packages.

PathHooks are placed into the list `sys.path_hooks`; like
`sys.meta_path`, the list is ordered and first one wins.

### The Takeaway

There's some confusion over the difference between the two objects, so
let's clarify one last time.

<em class="pointer">☞</em> Use a **meta_finder** (A Finder in
`sys.meta_path`) when you want to redefine the meaning of the import
string so it can search alternative paths that may have no reference to
a filesystem path found in `sys.path`; an import string could be
redefined as a location in an archive, an RDF triple of
document/tag/content, or table/row_id/cell, or be interpreted as a URL
to a remote resource.

<em class="pointer">☞</em> Use a **path_hook** (A function in
`sys.path_hooks` that returns a FileFinder) when you want to
re-interpret the meaning of an import string that refers to a module
object on or accessible by `sys.path`; PathHooks are important when you
want to add directories to sys.path that contain something _other than_
`.py`, `.pyc/.pyo`, and `.so` modules conforming to the Python ABI.

<em class="pointer">☝</em> A *MetaFinder* is typically constructed when
it is added to `sys.meta_path`; a *PathHook* instantiates a *FileFinder*
when the PathHook function lays claim to the path.  The developer
instantiates a MetaFinder before adding it to `sys.meta_path`; it's the
PathHook function that instantiates a FileFinder.

## Next

Note that PathHooks are for paths containing something _other than_ the
traditional (and hard-coded) source file extensions.  The purpose of a
heterogeneous source file finder and loader is to enable finding in
directories within `sys.path` that contain other source files syntaxes
_alongside_ those traditional sources.  I need to *eclipse* (that is,
get in front of) the default FileFinder with one that understands more
suffixes than those listed in either `imp.get_suffixes()` (Python 2) or
`importlib._bootstrap.SOURCE_SUFFIXES` (Python 3).  I need one that will
return the Python default loader if it encounters the Python default
suffixes, but will invoke *our own* source file loader when encountering
one of our suffixes.

We'll talk about loading next.
