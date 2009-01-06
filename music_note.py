#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, re, sys
import os, os.path
import locale
import string

import mutagen
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
#MP3(filename, ID3=EasyID3)

import encutils

MEDIACON_DIR = "/tmp/MediaCon/"
CACHE_DIR    = "Cache"
MUSIC_DIR    = "Music"
VIDEO_DIR    = "Video"
STAT_DIR     = "Stat"

ENCODING = locale.getpreferredencoding()

repair_tags = True

def MakeDirectory (dir):
    if not os.path.exists(dir):
        print "Creating dir " + dir
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
            MakeDirectory(self.root)
            MakeDirectory(self.cache)
            MakeDirectory(self.music)
        except:
            print "Fatal error while creating MediaCon dirs"
    def __dropCache(self):
        DeleteDir (self.cache)
    def __init__(self, root, cache, music, drop=False):
        self.root  = root
        self.cache = os.path.join(root, cache)
        self.music = os.path.join(root, cache, music)
        if drop:
            self.__dropCache()
        self.__initCache()
    def AddData (self, data):
        print data
        if not(os.path.exists(os.path.join(self.music, data['artist'])) and os.path.isdir(os.path.join(self.music, data['artist']))):
            os.mkdir(os.path.join(self.music, data['artist']))
        fh = open(os.path.join(self.music, data['artist'], data['album']), "a+")
        fh.write(data['title'].encode('utf-8') + "\n")
        fh.close()

cache = MediaCache(MEDIACON_DIR, CACHE_DIR, MUSIC_DIR)

##########################################################
        
def isascii(string):
    return not string or min(string) < '\x127'

def isMedia(x):
    try:
        media = mutagen.File(x)
    except:
        print "Can't parse file '", x, "'!"
        media = None
    if media: return media
    
def ID3TagsNormalized (id3):
    id3_tags = { "TIT2" : "title", "TPE1" : "artist", "TALB" : "album" }
    id3_info = { "artist" : "Unknown", "album" : "Unknown", "title" : "Unknown" }
    for tag in [k for k in id3_tags if k in id3.keys()]:
        id3_info[id3_tags[tag]] = id3[tag].text[0]
    return id3_info
    
def ID3Tags (id3,
             tags=["TIT2", "TPE1", "TALB"],
             Convert=True,
             tags_conv={ "TIT2" : "title", "TPE1" : "artist", "TALB" : "album" }):
    result = { 'artist' : 'Unknown', 'album' : 'Unknown', 'title' : 'Unknown' }
    for tag in [k for k in id3.keys() if k in tags]:
        if Convert == True:
            if tag in tags_conv:
                result[tags_conv[tag]] = id3[tag].text[0]
            else:
                result[tag] = id3[tag].text[0]
    return result

def RepairID3Tags (media):
    for tag in filter(lambda t: t.startswith("T"), media):
        frame = media[tag]
        # Skip non unicode fields:
        if isinstance(frame, mutagen.id3.TimeStampTextFrame):
            continue
        try:
            text = map(lambda x: x.encode('iso-8859-1').decode('CP1251'), frame.text)
        except (UnicodeError, LookupError):
            continue
        else:
            frame.text = text
            if min(map(isascii, text)):
                frame.encoding = 3
            else:
                frame.encoding = 1
        media[tag] = frame
    return media
    
def getTags (media):
    info = None
    print "META: " + media.mime[0]
    if media.mime[0] == 'audio/mp3':
        info = ID3Tags (media)
    elif media.mime[0] in ['audio/vorbis', 'audio/ogg']:
        info = { 'artist' : 'Unknown', 'album' : 'Unknown', 'title' : 'Unknown' }
        for tag in [k for k in info.keys()  if k in media.keys()]: info[tag] = media[tag][0]
    return info

def StoreMediaInfo (filename, mime, tags):
    1

def ParseMediaFiles (dirname, filters=None):
    if filters:
        allowed = re.compile(filters).search
    else:
        allowed = lambda x: 1
    for root, dirs, files in os.walk(dirname):
        files = [filename for filename in files if allowed(filename)]
        for filename in map(lambda x: os.path.join(root, x), files):
            media = isMedia(filename)
            if not media: continue
            print "Processing " + filename
            if media.mime[0] == 'audio/mp3':
                media = RepairID3Tags(media)
                if repair_tags:
                    try:
                        media.save(filename, v1=False)
                    except IOError:
                        print "Can't modify file " + filename
            tags = getTags(media)
            if tags: cache.AddData(tags)

def main ():
    args = sys.argv[1:]
    if not args:
        print "Be sure to set atleast one directory as argument"
        sys.exit(1)
    for directory in args:
        ParseMediaFiles(directory)

if __name__ == "__main__":
    main()
