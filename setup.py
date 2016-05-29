#!/usr/bin/python

import ast
import os
import re
import sys

try:
    from setuptools import setup, Command
except ImportError as excp:
    from distutils.core import setup, Command

from unittest import TestLoader, TextTestRunner


os.environ['COPY_EXTENDED_ATTRIBUTES_DISABLE'] = 'true'
os.environ['COPYFILE_DISABLE'] = 'true'


def _read_doc():
    """
    Parse docstring from file 'polyloader.py' and avoid importing
    this module directly.
    """
    with open('polyloader.py', 'r') as f:
        tree = ast.parse(f.read())
    return ast.get_docstring(tree)


def _read_attr(attr_name):
    """
    Parse attribute from file 'polyloader.py' and avoid importing
    this module directly.

    __version__, __author__, __contact__,
    """
    regex = attr_name + r"\s+=\s+'(.+)'"
    with open('polyloader.py', 'r') as f:
        match = re.search(regex, f.read())
    # Second item in the group is the value of attribute.
    return match.group(1)


class TestCommand(Command):
  """Run tests."""
  user_options = []

  def initialize_options(self):
    pass

  def finalize_options(self):
    pass


polyloader_version = _read_attr('__version__')
if 'bdist_msi' in sys.argv:
    polyloader_version, _, _ = polyloader_version.partition('-')


class TestCommand(Command):
  """Run tests."""
  user_options = []

  def initialize_options(self):
    pass

  def finalize_options(self):
    pass

  def run(self):
    test_suite = TestLoader().discover('./tests', pattern='*_test.py')
    test_results = TextTestRunner(verbosity=2).run(test_suite)


setup(name = 'polyloader',
    version = polyloader_version,
    description = 'Python artbitrary syntax import hooks',
    author = _read_attr('__author__'),
    author_email = _read_attr('__contact__'),
    url = 'https://github.com/elfsternberg/py-polymorphic-loader',
    keywords = ['python', 'import', 'language', 'hy', 'mochi'],
    classifiers = [
        'Development Status :: 3 - Alpha',
    	'Intended Audience :: Developers',
    	'Natural Language :: English',
    	'Operating System :: OS Independent',
    	'Programming Language :: Python',
    	'Topic :: Software Development :: Libraries :: Python Modules'],
    long_description = "\n".join(_read_doc().split('\n')),
    cmdclass={"test": TestCommand},
    py_modules = ['polyloader'],
    install_requires=[
          'future',
    ],
)
