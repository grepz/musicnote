#!/usr/bin/python
# -*- coding: utf-8 -*-


import os.path
import textwrap
from storm.locals import *

__all__ = ['Artist', 'Album', 'Track', 'MetaDBStorage', 'BaseMetaDBInterface']

DEF_STORAGE_PATH = '/tmp/'
DEF_DB_NAME      = 'MusicNote.db'

class BaseMetaDBInterface ():
    def __init__(self, tags):
        self.tags = tags

    def Tags(self):
        return self.tags.keys()

    def Values(self):
        return tags.values()

    def pprint(self):
        for key in (lambda k: k.sort() or k)(self.tags.keys()):
            print('| ' + key + ':\t' + self.tags[key])

class Artist(object):
    __storm_table__ = 'artist'
    id           = Int(primary=True)
    artist_name  = Unicode()
    artist_notes = Unicode()
    description  = Unicode()

    def __init__(self, name, notes=u'', description=u''):
        self.artist_name  = name
        self.artist_notes = notes
        self.description  = description

class Album(object):
    __storm_table__ = 'album'
    id             = Int(primary=True)
    artist_id      = Int()
    artist         = Reference(artist_id, Artist.id)
    album_name     = Unicode()
    album_notes    = Unicode()
    date_published = Date()

    def __init__(self, name, notes=u'', published=None):
        self.album_name     = name
        self.album_notes    = notes
        self.date_published = published
    
class Track(object):
    __storm_table__ = 'track'
    id          = Int(primary=True)
    album_id    = Int()
    album       = Reference(album_id, Album.id)
    track_name  = Unicode()
    track_notes = Unicode()
    location    = Unicode()
    length      = Int()
    metatype    = RawStr()
    style       = Unicode()

    def __init__(self, name, length, location, metatype, notes=u'', style=u''):
        self.track_name  = name
        self.track_notes = notes
        self.location    = location
        self.length      = length
        self.metatype    = metatype
        self.style       = style
        

Artist.albums = ReferenceSet(Artist.id, Album.id)
Artist.tracks = ReferenceSet(Artist.id, Track.id)

class MetaDBStorage():
    
    def ExportAs(self, export_type):
        1
    
    def __createTables(self):
        try:
            self.store.execute('CREATE TABLE artist '
                               '(id INTEGER PRIMARY KEY, '
                               'artist_name VARCHAR, artist_notes VARCHAR, description VARCHAR)')
            self.store.execute('CREATE TABLE album '
                               '(id INTEGER PRIMARY KEY, artist_id INTEGER, '
                               'album_name VARCHAR, album_notes VARCHAR, date_published DATE)')
            self.store.execute('CREATE TABLE track '
                               '(id INTEGER PRIMARY KEY, album_id INTEGER, '
                               'track_name VARCHAR, track_notes VARCHAR, location VARCHAR, '
                               'length INTEGER, metatype BYTEA, style VARCHAR)')
            self.store.commit()
        except:
            self.store.rollback()
            
    
    def __initStorage(self):
        print('Connecting to sqlite:' + self.db_path)
        self.database = create_database('sqlite:' + self.db_path)
        self.store    = Store(self.database)
        self.__createTables()

    def __init__(self, storage_path=DEF_STORAGE_PATH, db_name=DEF_DB_NAME):
        self.db_path = os.path.join(storage_path, db_name)
        self.__initStorage()

    def __AddArtist (self, artist_name):
        artist = Artist(artist_name)
        self.store.add(artist)
        return artist

    def __AddAlbum (self, album_name, artist_id):
        album = Album(album_name)
        album.artist_id = artist_id
        self.store.add(album)
        return album

    def __AddTrack (self, track_name, album_id):
        track = Track(track_name, 0, u'', '')
        track.album_id = album_id
        self.store.add(track)
        return track

    def AddData (self, tags):
        art_name = tags['artist']
        alb_name = tags['album']
        trk_name = tags['title']
        artist = self.store.find(Artist, Artist.artist_name == art_name).one()
        if (not artist):
            artist = self.__AddArtist(art_name)
            self.store.flush()
        album = self.store.find(Album, Album.album_name == alb_name, Album.artist_id == artist.id).one()
        if (not album):
            album = self.__AddAlbum(alb_name, artist.id)
            self.store.flush()
        track = self.store.find(Track, Track.track_name == trk_name, Track.album_id == album.id).one()
        if (not track):
            track = self.__AddTrack(trk_name, album.id)
            self.store.flush()
        self.store.commit()
        
