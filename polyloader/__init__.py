# -*- coding: utf-8 -*-
import sys

__author__ = 'Kenneth M. "Elf" Sternberg'
__email__ = 'elf.sternberg@gmail.com'
__version__ = '0.1.0'

if sys.version[0:2] == (2, 7):
    from ._python27 import install

if sys.version[0] >= 3:
    from ._python3 import install

__all__ = ['install']
