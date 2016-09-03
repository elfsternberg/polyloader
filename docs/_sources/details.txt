Details on Import and Polyloader
================================

Welcome to the Python Import ELI5!
**********************************

What is `import`?
-----------------

``import`` is a Python statement that finds a *module* that is accessible
by the currently running process, loads it, and makes its contents
available to the scope in which the statement was made.  A statement
like

``import django.db.models``

is looking for a module named ``django.db.models``. If the statement is
successful, ``django.db.models`` will be a variable name in the scope,
it will be a Python *object* (of ``class Module``, but that's not
important), and it will have functions, class constructors, variables
and constants.  These Python objects will be accessible through the dot
operator.

An alternative way of writing import statements is

``from django.utils import encoding``

And then the variable will just be ``encoding``.  The ``encoding``
module has a function for handling unicode-to-web translation.
Accessing it through the dot operator, it looks like this:

``ready_str = encoding.smart_str(unready_str)``

We call the parts of the import statement that describe the module the
*import string*.

``sys.path_hooks``: How does Python know where to look?
-------------------------------------------------------

That's what's funny.  Python has two independent ways of making sense of
of the import string.  The old system is based on the assumption that
everything is a filesystem, with folders and filenames.  This is called
the ``sys.path_hooks`` system.

In the old system, the parts of the import string would be split up, and
then a collection of directories would be scanned to see if the first
name in the import string could be matched with a subdirectory.  If it
could, that directory would be scanned until the last name on the import
string.  If that name was a *filename*, it would be loaded as a module.
If that name was a *directory* and that directory had a file named
``__init__.py``, then that file would be loaded as the module.

The ``sys.path_hooks`` array has a list of different methods for trying to
scan a filesystem for the parts of the import string.  A ``path_hook`` is
a function that takes a path to a directory; if it can handle the
contents of the directory, it returns a **Finder**, an object whose job
is to figure out how to load the module; if it can't, it returns an
ImportError exception.  The object that loads the module is called,
naturally, a **Loader**.

* To read more about **Finders**, see :ref:`eli5-finders`
* To read more about **Loaders**, see :ref:`eli5-loaders`
* To read more about **Path Hooks**, see :ref:`eli5-pathhooks`  

``sys.path``: What directories are searched?
--------------------------------------------

The list of directories is stored in an array, ``sys.path``.  This path is
initialized by Python when it starts up, but programs can modify it at
run-time to point to extra directories if they want.


``sys.meta_path``: What is the new system?
------------------------------------------

The new system is called ``sys.meta_path``, and it's an array of
**Finders**, objects that have one method, ``find_module(fullname)``.
It's an anything-goes API that gives developers the freedom to import
modules from anywhere: databases, archives, remote web resources, even
code written on-the-fly internally.  The new system can apply any
meaning at all to the import string.

In Python, the import string is offered to each object in
``sys.meta_path`` before being offered to each ``sys.path_hook``.  The
filesystem is typically the last finder tried.

To read more about **Meta Paths**, see :ref:`eli5-metapaths`

Is it different between Python 2 and Python 3?
---------------------------------------------

Python 3 moves almost everything about this process into python's
library, leaving only a bare minimum of functionality inside the Python
executable to load this library and run it.  When the Python developers
did that, they added a lot of functionality to make it easier to write
new import modules.  The old way still works, but there are now *Module
Specifications*, which are metadata about a module, and the old
``path_hooks`` system is now just a ``meta_path`` handler added to the
new system as the last resort.

To read more about **Module Specifications**, see :ref:`eli5-specs`

Does the old system still matter?
---------------------------------

Yes, for one reason: *iteration*.  Iteration is the ability to take a
path where you believe Python modules can be found, and list through
them.  This facility is useful for large frameworks where a user wants
to add new commands, or new objects, or new operations; Django uses this
facility a lot!  The ``pkgutil`` library depends upon Finders being able
to iterate their contents, and with the filesystem iterator, that means
being able to tell there's more than one kind of syntax in a directory.
