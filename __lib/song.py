from __lib.base import stdout, bold, warn, error, green, cyan, end_color, \
    read_json, dump_json, assert_py3, u
from __lib.music_tag import m_load_file


class Song(object):
    def __init__(self, root=None, project=None, artist=None, album=None,
                 path=None, song_f=None,
                 autoload=True, tags=None, debug=False, **kwargs):
        if path:
            self._path = path
            self._file = song_f
            self._full_path = path + '/' + song_f
        elif root and project and artist and album:
            self._path = (root + '/' + project + '/' +
                          artist + '/' + album + '/')
            self._file = song_f
            self._full_path = self._path + '/' + song_f
        elif song_f:
            # in this case song_f /is/ the full path
            self._path = None
            self._file = None
            self._full_path = song_f
        else:
            self._path = None
            self._file = None
            self._full_path = None
        self.is_json = song_f.lower().endswith('.json')
        if autoload:
            self.tags = self.load(debug=debug)
        elif tags:
            self.tags = tags
        else:
            self.set_tags(debug, **kwargs)
        self.debug = debug

    def __str__(self):
        return str(self.tags)

    def path(self):
        return self._path

    def name(self, fully_qualified=False):
        if fully_qualified or self._file is None:
            return self._full_path
        else:
            return self._file

    def full_path(self):
        return self._full_path

    def debug_out(self, *args, **kwargs):
        if self.debug:
            end_color()
            stdout(*args, **kwargs)

    @staticmethod
    def get_tag_keys(extended=False, capitalize=True):
        # Mind, Windows applies camel-case tags (and does Album artist with
        # space) ; musictag converts to uppercase internally

        if capitalize:  # keep this True
            tags = ['TITLE', 'TRACKNUMBER', 'ALBUM', 'ARTIST', 'ALBUMARTIST']
            if extended:
                tags.extend(['#BITRATE', '#CODEC', '#LENGTH', '#CHANNELS',
                             '#BITSPERSAMPLE', '#SAMPLERATE'])
                tags.extend(['ARTWORK', 'COMMENT', 'COMPILATION', 'COMPOSER',
                             'DISCNUMBER', 'GENRE', 'LYRICS', 'YEAR',
                             'TOTALDISCS', 'TOTALTRACKS'])
        else:
            tags = ['Title', 'Tracknumber', 'Album', 'Artist', 'Album artist']
            if extended:
                tags.extend(['#bitrate', '#codec', '#length', '#channels',
                             '#bitspersample', '#samplerate'])
                tags.extend(['Artwork', 'Comment', 'Compilation', 'Composer',
                             'Discnumber', 'Genre', 'Lyrics', 'Year',
                             'Totaldiscs', 'Totaltracks'])

        return tags

    # @staticmethod
    # def get_printed_tag(tag):
    #     return 'Contrib. artist(s)' if tag == 'Artist' else tag

    def get(self, tag):
        assert tag == tag.upper()
        assert tag != 'ALBUM ARTIST'  # if windows style
        if self.is_json:
            return self.tags.get(tag) or ''
        else:
            return u(self.tags.get(tag)) or ''  # mind, don't change to ''
            #                                     withing the get(tags)

    def get_tags(self, extended=False):
        d = {}
        for tag in self.get_tag_keys(extended):
            d[tag] = self.get(tag)
        return d

    def get_track_nbr_as_string(self, default='1', verbose=False):
        t = self.get('TRACKNUMBER')
        if not t and default is not None:
            if verbose:
                warn(self.get('TITLE'), 'has no track number, '
                                        'assuming track #1')
            t = default
        return t

    def parse_track_nbr(self, track=None):
        t = track if track else self.get_track_nbr_as_string()
        if t is None:
            return None, None
        elif '/' in t:
            t = t.split('/')
            track = int(t[0])
            total_tracks = int(t[1])
            return track, total_tracks
        else:
            # noinspection PyTypeChecker
            return int(t), None

    def set(self, tag, value, save=False, dryrun=True,
            straight_overwrite_artist=False):
        self.debug_out('Song.set(' + tag + '->' + value + ')', save, dryrun,
                       straight_overwrite_artist)
        assert tag == tag.upper()
        assert tag != 'ALBUM ARTIST'  # if windows style
        if tag == 'ALBUMARTIST':
            if straight_overwrite_artist:
                self.debug_out('ARTIST.overwrite', value)
                self.tags['ARTIST'] = value
            else:
                album_artist = self.get(tag)
                if album_artist:
                    # fix Contributing Artists as well
                    contributing_artists = self.get('ARTIST')
                    if value in contributing_artists:
                        self.debug_out('ARTIST.replace', album_artist,
                                       'with', value)
                        self.tags['ARTIST'] = contributing_artists.replace(
                            album_artist, value)
        self.tags[tag] = value
        if save:
            self.save(dryrun)

    def set_tags(self, save=False, dryrun=True, **kwargs):
        for key, item in kwargs.items():
            key = key.upper()
            if item is None or item.lower() == 'none':
                self.remove(key)
            else:
                self.set(key, item)
        if save:
            self.save(dryrun)
        return self

    def remove(self, tag, save=False, dryrun=True):
        assert tag == tag.upper()
        assert tag != 'ALBUM ARTIST'  # if windows style
        del self.tags[tag]
        if save:
            self.save(dryrun)

    def load(self, exit_on_exc=True, debug=False):
        try:
            if self.is_json:
                self.tags = read_json(self.full_path())
            else:
                self.tags = m_load_file(self.full_path())

            return self.tags

        except Exception as e:
            error('Couldn\'t load', self.full_path, fatal=exit_on_exc, exc=e,
                  debug=debug)
            return None

    def save(self, dryrun=True, file_path=None):
        if not dryrun:
            if not file_path:
                assert self.full_path()
            if self.is_json:
                dump_json(self.tags, to_file=file_path or self.full_path())
            else:
                self.tags.save()

    def diff(self, other, my_name=None, other_name=None,
             print_all_diffs=False, extended=False,
             print_on_diff=True, print_on_diff_f=None, debug=False):
        diff = False
        tags = self.get_tag_keys(extended)
        my_name = my_name or self.name()
        other_name = other_name or other.name()
        for tag in tags:
            if self.get(tag) == other.get(tag):
                if debug:
                    stdout(tag, 'equal:',
                           self.get(tag), '(' + my_name + ') ==',
                           other.get(tag), '(' + other_name + ')')
            else:
                if not diff and print_on_diff:
                    if print_on_diff_f:
                        stdout(print_on_diff_f)
                    else:
                        cyan(tag, 'diff:',
                             self.get(tag), '(' + my_name + ') !=',
                             other.get(tag), '(' + other_name + ')')
                diff = True
                if not print_all_diffs:
                    break
        return diff

    def echo(self):
        stdout('[' + self.get('TRACKNUMBER'), self.get('ALBUM') + ']', end=' ')
        bold(self.get('TITLE'), end=' ')
        stdout('[' + self.get('ALBUMARTIST') + ']')

    def stdout(self, extended=False, highlight_title=False):
        for tag in self.get_tag_keys(extended):
            if highlight_title and tag == 'TITLE':
                bold('TITLE:', self.get(tag))
            else:
                stdout(tag, ':', self.get(tag))
        stdout()

    def stdout_json(self, extended=False, as_pprint=False, to_file=None):
        d = {}
        for tag in self.get_tag_keys(extended):
            d[tag] = self.get(tag)
        dump_json(d, pp=as_pprint, to_file=to_file)

    def print_tags(self, detailed=False,
                   as_json=False, as_pprint=False, to_file=None,
                   extended=False, header=True,
                   subscript=None, highlight_title=False):
        if header and not to_file:
            stdout()
            if subscript:
                green(self.full_path(), end='')
                cyan(' (' + subscript + ')')
            else:
                green(self.full_path())
        track = self.get('TRACKNUMBER')
        fix_track = False
        if track.startswith('T'):
            track = track[1:]
            fix_track = True
        if fix_track:
            self.set('TRACKNUMBER', track)
        if detailed:
            self.stdout(extended, highlight_title)
        elif as_json or as_pprint:
            self.stdout_json(extended, as_pprint, to_file)
        else:
            self.echo()
