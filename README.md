__polyloader__ is a python module to hook into Python's import machinery
and insert your own syntax parser/recognizer. Importlib uses filename
suffixes to recognize which compiler to use, but is internally
hard-coded to only recognize ".py" as a valid suffix.

## To use:

Import polyloader in your python script's launcher or library, as well
as the syntax compiler(s) you plan to use. For example, if you have
[Mochi](<https://github.com/i2y/mochi>) and
[Hy](<http://docs.hylang.org/en/latest/>) installed, and you wanted to
write a Django app, edit manage.py and add the following lines at the
top:

~~~~
 from mochi.main import compile_file as mochi_compile
 from hy.importer import ast_compile as hy_compile
 from polyloader import polyimport
 polyimport(mochi_compile, ['.mochi'])
 polyimport(hy_compile, ['.hy'])}
~~~~

Now your views can be written in Hy and your models in Mochi, and
everything will just work.

## Dependencies

polymorph is self-contained. It has no dependencies other than Python
itself and your choice of language.