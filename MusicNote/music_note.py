# -*- coding: utf-8 -*-

#  music_note.py -- ondisk Music data crawler with a number of features
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

# TODO:
# 1. Check if files are converted/translated/moved, if not, signal(log file,
#    stdout)
# 2. Merge music titles(graphical/console interface)
# 3. File transmormation format
# 4. Choose what tags to repair
# 5. Check for bugs, legion is their name. :)
# 6. Complete GUI design and implementation
# 7. Extend tags

import sys
#import traceback
import re
import locale
import string
import os, os.path
import getopt

try:
    import encutils

    import mutagen
    from mutagen.mp3 import MP3
    from mutagen.easyid3 import EasyID3

    # Here we define routines to store parsed meta data
    import storage

    # Here is code that creates simple cache for meta data
    from cache import *
    # Lexical utils
    import lexical

    from tools import *

except ImportError, err:
    print "Error while importing. %s" % err
    exit(1)

# Media storage, implemented as sqlite3 db
meta_store  = None
# Cache, where all files goes
cache_store = None

# Command line options
repair_tags       = False
repair_filenames  = False
fill_database     = False
verbose           = False

ENCODING = locale.getpreferredencoding()

# Encodings used
enc_from = 'CP1251'
enc_to   = 'iso-8859-1'

# Target directory
target_dir = None
# Database path
db_path = None

# mp3 tags to ordianry tags conversion
id3_tags = { 'TIT2' : 'title',
             'TPE1' : 'artist',
             'TALB' : 'album' }

# Default values for tags
conv_tags = { 'artist' : u'Unknown',
              'album'  : u'Unknown',
              'title'  : u'Unknown' }

##########################################################

def isascii(string):
    return not string or min(string) < '\x127'

def isMedia(x):
    try:
        media = mutagen.File(x)
    except:
        print 'Can\'t parse file "', x, '"!'
        media = None
    if media: return media

# TODO: Check unicode with type()
def check_tags_exists (probe, prot):
    '''Check if tags in prototype exists in probe'''
    if [k for k in prot if k not in probe]:
        return False
    return True

def ParseMediaDB (store):
    pass

# [check(k) for k in a if k in tags]

def ID3TagsNormalized (id3):
    global id3_tags, conv_tags
    id3_info = conv_tags
    for tag in [k for k in id3_tags if k in id3.keys()]:
        id3_info[id3_tags[tag]] = id3[tag].text[0]
    return id3_info
    
def ID3Tags (id3,
             tags=['TIT2', 'TPE1', 'TALB'],
             Convert=True,
             tags_conv=id3_tags):
    result = conv_tags
    for tag in [k for k in id3.keys() if k in tags]:
        if Convert == True:
            if tag in tags_conv:
                result[tags_conv[tag]] = id3[tag].text[0]
            else:
                result[tag] = id3[tag].text[0]
    return result

def RepairID3Tags (media):
    for tag in filter(lambda t: t.startswith('T'), media):
        frame = media[tag]
        # Skip non unicode fields:
        if isinstance(frame, mutagen.id3.TimeStampTextFrame):
            continue
        try:
            # TODO: Try to guess
            text = map(lambda x: x.encode(enc_to).decode(enc_from), frame.text)
        except (UnicodeError, LookupError):
            continue
        else:
            frame.text = text
            # Check and handle ASCII
            if min(map(isascii, text)):
                frame.encoding = 3
            else:
                frame.encoding = 1
        media[tag] = frame
    return media
    
def getTags (media):
    global conv_tags
    info = None
    # There is difference in tags names across mp3 and ogg/vorbis
    if media.mime[0] == 'audio/mp3':
        info = ID3Tags (media)
    elif media.mime[0] in ['audio/vorbis', 'audio/ogg']:
        info = conv_tags
        for tag in [k for k in info.keys() if k in media.keys()]:
            info[tag] = media[tag][0]
    return info

def ParseMediaFiles (dirname, filters=None):
    global meta_store, cache_store, repair_tags, verbose, target_dir
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
            # If mp3 convert tags names to ogg like
            if media.mime[0] == 'audio/mp3':
                media = RepairID3Tags(media)
                # Push changes to files
                if repair_tags:
                    try:
                        # FIXME: Deprecation warning, handle this
                        media.save(filename, v1=False)
                    except IOError:
                        print 'Can\'t modify file ' + filename
            # FIXME: Restructure
            tags = getTags(media)
            if tags == None: continue
            if repair_filenames:
                cache_store.AddFile (tags, filename)
            if fill_database:
                d_print (verbose, 'Tags %s to DB' % tags)
                meta_store.AddData(tags)

########################################

def Usage ():
    print '''Usage: %s <options> <directories>
    -t|--repairtags   - Repair tags
    -f|--repairfiles  - Repair file names
    -d|--targetdir    - Target directory
    -e|--encoding     - Default FROM encoding
    -h|--help         - Show this text
    -b|--filldatabase - Set encoding
    -s|--dbpath       - Path where sqlite DB will be created
    -v|--verbose      - Verbose output''' % sys.argv[0]
    exit(0)

def main (argv):
    global meta_store, cache_store
    global repair_tags, repair_filenames, fill_database
    global verbose
    global target_dir
    global db_path
    
    try:
        opts, args = getopt.getopt(argv, 'hvtfbd:e:s:',
                                   ['help', 'verbose', 'repairtags',
                                    'repairfiles', 'filldatabase',
                                    'targetdir=', 'encoding=',
                                    'dbpath='])
    except getopt.GetoptError:
        Usage()
        sys.exit(1)
    for opt,arg in opts:
        if opt in ('-h', '--help'):
            Usage()
        elif opt in ('-t', '--repairtags'):
            repair_tags = True
        elif opt in ('-f', '--repairfiles'):
            repair_filenames = True
        elif opt in ('-b', '--filldatabase'):
            fill_database = True
        elif opt in ('-e', '--encoding'):
            # TODO: Validate
            enc_from = arg
        elif opt in ('-d', '--targetdir'):
            target_dir = arg
        elif opt in ('-v', '--verbose'):
            verbose = True
        elif opt in ('-s', '--dbpath'):
            db_path = arg

    if args == []:
        print 'Be sure to set atleast one directory as argument'
        Usage()
    if (repair_filenames == True) and (target_dir == None):
        print '''Set target directory, where new filenames will be created.
Warning. Do not choose the same directory, where original files lies!'''
        exit(1)
    if (fill_database) == True and (db_path == None):
        print '''Set database path.'''
        exit(1)

    d_print (verbose, 'Directories selected: %s', args)
    d_print (verbose, '''Repair tags: %s
Repair files: %s
FillDB: %s''', repair_tags, repair_filenames, fill_database)
    if fill_database:
        meta_store  = storage.MetaDBStorage(db_path)
    if repair_filenames:
        cache_store = MusicStorage(target_dir, drop=False)
    for directory in args:
        ParseMediaFiles(directory)

if __name__ == '__main__':
    main(sys.argv[1:])
