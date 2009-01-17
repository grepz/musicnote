#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

package = 'MusicNote'
version = '0.1-beta1'

py_modules = ['MusicNote.tools',
              'MusicNote.storage',
              'MusicNote.lexical'
              ]

setup (name=package, version=version,
       description='Small ondisk music collection organizer',
       author='Stanislav M. Ivankin',
       author_email='stas@concat.info',
       url='http://concat.info/musicnote/',
       packages=['MusicNote', 'MusicNote.tests'],
       py_modules=py_modules
       )
