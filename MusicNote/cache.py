#!/usr/bin/python
# -*- coding: utf-8 -*-

#  cache.py -- ondisk Music data crawler with a number of features
#
#  Copyright 2009 Stanislav M. Ivankin <stas@concat.info>
#
#  This file is part of musicnote.
#
#  musicnote is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  musicnote is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with musicnote.  If not, see <http://www.gnu.org/licenses/>.

import os, os.path
import shutil

def make_dir (dir):
    if not os.path.exists(dir):
        print 'Creating dir ' + dir
        os.mkdir(dir)
    elif not os.path.isdir(dir):
        raise Exception('MediaCon', 'Can\'t create directory' + dir)
    return dir

def make_dir_r (dir):
    fullpath = ''
    for d in dir.split('/'):
        fullpath = os.path.join('/', fullpath, d)
        make_dir (fullpath)

#def make_dir_r (dir):
#    reduce (lambda x,y: make_dir (os.path.join('/', x, y)), dir.split('/', 1))

def delete_dir(dir):
    for name in os.listdir(dir):
        file = os.path.join(dir, name)
        if not os.path.islink(file) and os.path.isdir(file):
            delete_dir(file)
        else:
            os.remove(file)
    os.rmdir(dir)

class MusicStorageInterface ():
    multibyte = True
    
    def check_filepath (self, path):
        try:
            make_dir_r(path[:path.rindex('/')])
        except (ValueError):
            print ('Seems strange path to me: %s' % path)
            return False
        return True
    
    def __make_media_filepath (self, tags, ext):
        if self.multibyte == False:
            tags = dict([(key, lexical.translit_str(val).title())
                         for (key, val) in tags.items()])
        return os.path.join(tags['artist'],
                            tags['album'],
                            ' - '.join([tags['artist'],
                                        tags['album'],
                                        tags['title']]) + ext)
    
    def convert_filename (self, tags, filename):
        ext = None
        try:
            ext = filename[filename.rindex('.'):]
        except (ValueError):
            ext = ''
        return self.__make_media_filepath (tags, ext)

    def cache_file (self, src, dst, move=False):
        '''Dummy functyion'''
        if os.path.exists (dst):
            return
        if move:
            shutil.move (src, dst)
        else:
            shutil.copy(src, dst)

class MusicStorage(MusicStorageInterface):
    storage_dir = None
    
    def __initStorage(self):
        try:
            make_dir_r (self.storage_dir)
        except:
            print 'Fatal error while creating MediaCon dirs'
            
    def __dropStorage(self):
        if os.path.isdir(self.storage_dir):
            print 'Deleting dir ', self.storage_dir
            delete_dir (self.storage_dir)
        
    def __init__(self, dir, drop=True):
        self.storage_dir = dir
        if drop:
            self.__dropStorage()
        self.__initStorage()

    def AddFile (self, tags, src):
        dst = os.path.join (self.storage_dir,
                            self.convert_filename (tags, src))
        if self.check_filepath (dst):
            self.cache_file(src, dst)

#     def AddData (self, data):
#         if not(os.path.exists(
#             os.path.join(self.music, data['artist'])) and
#                os.path.isdir(os.path.join(self.music, data['artist']))):
#             os.mkdir(os.path.join(self.music, data['artist']))
#         fh = open(os.path.join(self.music, data['artist'], data['album']), "a+")
#         fh.write(data['title'].encode('utf-8') + "\n")
#         fh.close()

