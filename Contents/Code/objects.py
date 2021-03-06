from routing import route_path, function_path, quote
from utils import normalize


class Objects(object):
    def __init__(self, host):
        self.host = host

    @property
    def client(self):
        return self.host.client

    def get(self, item):
        item_class = getattr(item, '__class__', None)

        if item_class is None:
            Log.Debug('Unable to retrieve class from item: %s', item)
            return None

        name = getattr(item_class, '__name__', None)

        if name == 'Artist':
            return self.artist(item)

        if name == 'Album':
            return self.album(item)

        if name == 'Track':
            return self.track(item)

        if name == 'Playlist':
            return self.playlist(item)

        Log.Debug('Unknown object with name: %s, type: %s' % (name, type(item)))
        return None

    def artist(self, artist):
        cover_url = self.image(artist.portraits)

        return DirectoryObject(
            key=route_path('artist', artist.uri),
            #rating_key=artist.uri,

            title=normalize(artist.name),

            art=cover_url,
            thumb=cover_url or R('placeholder-artist.png')
        )

    def album(self, album):
        title = normalize(album.name)

        # TODO album years
        #if Prefs["displayAlbumYear"] and album.getYear() != 0:
        #    title = "%s (%s)" % (title, album.getYear())

        cover_url = self.image(album.covers)

        track_count = None

        if album.discs:
            track_count = len(album.discs[0].tracks)

        return DirectoryObject(
            key=route_path('album', album.uri),
            #rating_key=album.uri,

            title=title,
            tagline=', '.join([normalize(ar.name) for ar in album.artists]),

            #track_count=track_count,

            art=cover_url,
            thumb=cover_url,
        )

    def track(self, track, index=None):
        rating_key = track.uri

        if index is not None:
            rating_key = '%s::%s' % (track.uri, index)

        cover_url = self.image(track.album.covers)

        return TrackObject(
            items=[
                MediaObject(
                    parts=[PartObject(
                        key=self.client.track_url(track),
                        duration=int(track.duration)
                    )],
                    duration=int(track.duration),
                    container=Container.MP3,
                    audio_codec=AudioCodec.MP3
                )
            ],

            key=route_path('metadata', str(track.uri)),
            rating_key=quote(rating_key),

            title=normalize(track.name),
            album=normalize(track.album.name),
            artist=', '.join([normalize(ar.name) for ar in track.artists]),

            index=int(track.number),
            duration=int(track.duration),

            art=cover_url,
            thumb=cover_url
        )

    @classmethod
    def playlist(cls, item):
        if item.uri and item.uri.type == 'group':
            # (Playlist Folder)
            return DirectoryObject(
                key=route_path('your_music/playlists', group=item.uri, title=normalize(item.name)),
                title=normalize(item.name),
                thumb=R("placeholder-playlist.png")
            )

        cover_url = None

        if item.image and item.image.file_uri:
            # Ensure we don't use invalid image uris
            if len(item.image.file_uri.code) == 27:
                cover_url = cls.image([item.image])

        return DirectoryObject(
            key=route_path('playlist', item.uri),
            title=normalize(item.name),
            thumb=cover_url or R('placeholder-playlist.png')
        )

    @staticmethod
    def image(covers):
        if covers and covers[-1]:
            # TODO might want to sort by 'size' (to ensure this is correct in all cases)
            # Pick largest cover
            return function_path('image.png', uri=covers[-1].file_url)

        Log.Info('Unable to select image, available covers: %s' % covers)
        return None
