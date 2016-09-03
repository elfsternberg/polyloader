Synopsis
--------

**Polyloader** is a python module that extends the Python `import`
statement to enable the discovery and loading of heterogenous source
code packages.

Say What? In English this time
-------------------------------

The ``import`` statement is how the Python interpreter finds a module
written in Python and loads it, turning it into variables, executable
functions, constructable classes, and other Python objects, and then
exposes those objects to the currently running program.

The ``import`` statement has long been extensible so that things other
than Python code could be imported, but this feature has always had two
limitations:

1. It's annoyingly hard to write an importer. (Believe me. Polyloader
   *is* one!)
2. For filesystem-based modules (which is 99% of them) Python's importer
   only understands one loader type per directory.  It's not possible to
   store code or data written in something other than Python in the same
   directory with Python module code and load it via ``import``.

The former requires a certain degree of abstraction and thought.  For
the latter, most people ignore the problem and load module configuration
files written in JSON or YAML or whatever directly.  This is fine,
except when you want to write in one of Python's extended languages like
Hy or Coconut in a framework like Django, Flask or Glitch.

**Polyloader** eliminates these limitations.

What's the real problem?
------------------------

The real problem is that Python's traditional extensions, ``.py``,
``.pyc/.pyo``, and ``.so/.dll`` files, are hard-coded in Python.  In
Python 2, they're in the ``imp`` builtin; In Python 3, they're defined
in a private section of `importlib`.  Either way, they're not accessible
for modification and extension.

This problem is made harder by the ``pkglib`` module, which is part of
Python's standard library.  This module uses ``inspect.getmoduleinfo``,
which again only recognizes the usual extensions.  Which means you can't
list multilingual modules either; this hampers the development of Django
management commands in a syntax other than Python.

What the solution?
------------------

At its heart, the Python import system runs two different internal
mechanisms to figure out what the *import string* (the dotted terms
after the word "import") "means."  Each mechanism has one or more
*finders*, and the first finder to report "I have a *loader* that knows
what that import string means" wins.

The very last finder is for the filesystem.  The solution is to get in
front of that finder with one that can handle all the other syntax
loaders *and* knows how to fall back on the last one for those files the
last one handles.

That's what ``polyloader`` does.  

