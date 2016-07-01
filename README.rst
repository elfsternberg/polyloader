Synopsis
--------

**Polyloader** is a python module that enables the discovery and loading
of heterogenous source code packages.  This discovery and loading is
critical to the functioning of other programming languages that use the
Python AST and Python interpreter, languages such as Hy, Doge, and
Mochi.

Problem Statement
-----------------

The Python module loader system is hard-coded to prevent the discovery
of heterogenous source code packages.  From Python 2.6 through the
current (as of this writing) Python 3.5, the import mechanism allows for
the creation of file finders and importers that would transform Python's
import syntax into a *path,* assert whether or not that path could be
made to correspond to a *syntax object*, and then attempt to *load* that
syntax object as a Python module.  Python *packages*, however, are
assumed to be uniformly made up of Python syntax objects, be they
**.py** source files, **.pyc/.pyo** bytecode, or **.so/.dll** files with
an exposed Python-to-C API.  In Python 2 these suffixes are hard-coded
into the source in the **imp** builtin module; in Python 3 these
suffixes are constants defined in a private section of **importlib**; in
either case, they are unavailable for modification.  This lack of access
to the extensions list prevents the *discovery* of heterogenous source
code packages.

The discovery mechanism is outlined in Python's **pkgutil** module;
features such as **pkgutil.iter_modules** do not work with heterogenous
source code, which in turn means that one cannot write, for one
important example, Django management commands in an alternative syntax.

**polyloader** is a Python module that intercepts calls to the default
finder, loader, and package module iterator, and if the path resolves to
an alternative syntax, provide the appropriate finder, loader and
iterator.  **polyloader** is different from traditional importlib shims
in that it directly affects the default source file loader, and thus
allows for the discovery and importation of suffixes not listed in
Python's defaults.

To use:
-------

Import polyloader in your python script's launcher or library, as well
as the syntax compiler(s) you plan to use. For example, if you have
`Mochi <https://github.com/i2y/mochi>`__ and
`Hy <http://docs.hylang.org/en/latest/>`__ installed, and you wanted to
write a Django app, edit manage.py and add the following lines at the
top:

::

     from mochi.main import compile_file as mochi_compile
     from hy.importer import ast_compile as hy_compile
     from polyloader import polyimport
     polyimport(mochi_compile, ['.mochi'])
     polyimport(hy_compile, ['.hy'])}

Now your views can be written in Hy and your models in Mochi, and
everything will just work.

Dependencies
------------

polymorph is self-contained. It has no dependencies other than Python
itself and your choice of language.
