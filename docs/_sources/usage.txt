=====
Usage
=====

Import polyloader in your python script's launcher or library, as well
as the syntax compiler(s) you plan to use. For example, if you have
`Mochi <https://github.com/i2y/mochi>`__ and `Hy
<http://docs.hylang.org/en/latest/>`__ installed, and you wanted to
write a Django app, edit manage.py and add the following lines at the
top:

::

     from mochi.main import compile_file as mochi_compile
     from hy.importer import ast_compile as hy_compile
     import polyloader
     polyloader.install(mochi_compile, ['.mochi'])
     polyloader.install(hy_compile, ['.hy'])}

Now your views can be written in Hy and your models in Mochi, and
everything will just work.

