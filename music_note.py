#!/usr/bin/python
# -*- coding: utf-8 -*-

#     music_note.py -- ondisk Music data crawler with a number of features
#
#     Copyright 2009 Stanislav M. Ivankin <stas@concat.info>
#
#     This file is part of musicnote.
#
#     musicnote is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     musicnote is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with musicnote.  If not, see <http://www.gnu.org/licenses/>.


import sys
import re
import locale
import string
import os, os.path

import mutagen
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

import encutils

# Here we define routines to store parsed meta data
import storage
# Here is code that creates simple cache for meta data
import cache

repair_tags = True

ENCODING = locale.getpreferredencoding()

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
    id3_info = { "artist" : u'Unknown', u'album' : u'Unknown', "title" : u'Unknown' }
    for tag in [k for k in id3_tags if k in id3.keys()]:
        id3_info[id3_tags[tag]] = id3[tag].text[0]
    return id3_info
    
def ID3Tags (id3,
             tags=["TIT2", "TPE1", "TALB"],
             Convert=True,
             tags_conv={ "TIT2" : "title", "TPE1" : "artist", "TALB" : "album" }):
    result = { 'artist' : u'Unknown', 'album' : u'Unknown', 'title' : u'Unknown' }
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
            # TODO: Do decode with guessing or asking user
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
    # There is difference in tags names across mp3 and ogg/vorbis
    if media.mime[0] == 'audio/mp3':
        info = ID3Tags (media)
    elif media.mime[0] in ['audio/vorbis', 'audio/ogg']:
        info = { 'artist' : 'Unknown', 'album' : 'Unknown', 'title' : 'Unknown' }
        for tag in [k for k in info.keys()  if k in media.keys()]: info[tag] = media[tag][0]
    return info

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
            print filename
            if media.mime[0] == 'audio/mp3':
                media = RepairID3Tags(media)
                if repair_tags:
                    try:
                        media.save(filename, v1=False)
                    except IOError:
                        print "Can't modify file " + filename
            tags = getTags(media)
#            print tags
            if tags:
                meta_store.AddData(tags)
#                test = storage.BaseMetaDBInterface(tags)
#                test.pprint()

########################################

meta_store = storage.MetaDBStorage()

def main ():
    args = sys.argv[1:]
    if not args:
        print "Be sure to set atleast one directory as argument"
        sys.exit(1)
    for directory in args:
        ParseMediaFiles(directory)

if __name__ == "__main__":
    main()
