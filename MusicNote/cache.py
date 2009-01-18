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

def MakeDir (dir):
    if not os.path.exists(dir):
        print 'Creating dir ' + dir
        os.mkdir(dir)
    elif not os.path.isdir(dir):
        raise Exception('MediaCon', 'Can\'t create directory' + dir)
    return dir

def MakeDirR (dir):
    fullpath = ''
    for d in dir.split('/'):
        fullpath = os.path.join('/', fullpath, d)
        MakeDir (fullpath)

#def MakeDirR (dir):
#    reduce (lambda x,y: MakeDir (os.path.join('/', x, y)), dir.split('/', 1))

def DeleteDir(dir):
    for name in os.listdir(dir):
        file = os.path.join(dir, name)
        if not os.path.islink(file) and os.path.isdir(file):
            DeleteDir(file)
        else:
            os.remove(file)
    os.rmdir(dir)


class MusicStorageInterface ():

    def __make_media_filepath (tags, ext, multibyte=True):
        if multibyte == None:
            tags = dict([(key, lexical.translit_str(val).title())
                         for (key, val) in tags.items()])
            return os.path.join(target_dir, tags['artist'],
                                tags['album'],
                                ' - '.join([tags['artist'],
                                            tags['album'],
                                            tags['title']]) + ext)
    
    def RepairFilename (tags, filename):
        ext = None
        try:
            ext = filename[filename.rindex('.'):]
        except (ValueError):
            ext = ''
        return make_media_filepath (tags, ext, multibyte=True)    


class MusicStorage(MusicStorageInterface):
    storage_dir = None
    
    def __initStorage(self):
        try:
            MakeDirR (self.storage_dir)
        except:
            print 'Fatal error while creating MediaCon dirs'
            
    def __dropStorage(self):
        if os.path.isdir(self.storage_dir):
            print "Deleting dir ", self.storage_dir
            DeleteDir (self.storage_dir)
        
    def __init__(self, dir, drop=True):
        self.storage_dir = dir
        if drop:
            self.__dropStorage()
        self.__initStorage()

cache = MusicStorage("/tmp/musicdir")


#     def AddData (self, data):
#         if not(os.path.exists(
#             os.path.join(self.music, data['artist'])) and
#                os.path.isdir(os.path.join(self.music, data['artist']))):
#             os.mkdir(os.path.join(self.music, data['artist']))
#         fh = open(os.path.join(self.music, data['artist'], data['album']), "a+")
#         fh.write(data['title'].encode('utf-8') + "\n")
#         fh.close()

