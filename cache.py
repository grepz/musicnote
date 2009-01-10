#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, os.path

import mutagen
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

MEDIACON_DIR = '/tmp/MediaCon/'
CACHE_DIR    = 'Cache'
MUSIC_DIR    = 'Music'
VIDEO_DIR    = 'Video'
STAT_DIR     = 'Stat'

def MakeDir (dir):
    if not os.path.exists(dir):
        print 'Creating dir ' + dir
        os.mkdir(dir)
    elif not os.path.isdir(dir):
        raise Exception('MediaCon', 'Can\'t create directory' + dir)

def DeleteDir(dir):
    for name in os.listdir(dir):
        file = os.path.join(dir, name)
        if not os.path.islink(file) and os.path.isdir(file):
            DeleteDir(file)
        else:
            os.remove(file)
    os.rmdir(dir)
    
class MediaCache():
    def __initCache(self):
        try:
            MakeDir(self.root)
            MakeDir(self.cache)
            MakeDir(self.music)
        except:
            print 'Fatal error while creating MediaCon dirs'
    def __dropCache(self):
        DeleteDir (self.cache)
    def __init__(self, root=MEDIACON_DIR, cache=CACHE_DIR, music=MUSIC_DIR, drop=False):
        self.root  = root
        self.cache = os.path.join(root, cache)
        self.music = os.path.join(root, cache, music)
        if drop:
            self.__dropCache()
        self.__initCache()
    def AddData (self, data):
        if not(os.path.exists(os.path.join(self.music, data['artist'])) and os.path.isdir(os.path.join(self.music, data['artist']))):
            os.mkdir(os.path.join(self.music, data['artist']))
        fh = open(os.path.join(self.music, data['artist'], data['album']), "a+")
        fh.write(data['title'].encode('utf-8') + "\n")
        fh.close()

