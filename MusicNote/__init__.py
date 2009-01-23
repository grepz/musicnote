# -*- coding: utf-8 -*-

__package__ = 'MusicNote'
__version__ = '0.1-beta1'

try:
    import pkg_resources
    pkg_resources.declare_namespace('musicnote')
except ImportError:
    print "Whoops"


