from __lib.base import stdout, green, yellow, u, end_color, warn, error, \
    start_bold, make_dir, get_env_var, get_home, filter_by, \
    assert_path_exists, print_path, assure_not_endswith, new_file, is_file
from __lib.song import Song

DEFAULT_ROOT = None
DEFAULT_MUSIC_ROOT = 'Music'

DEFAULT_ALBUM_ART_ROOT = None
DEFAULT_ALBUM_ART_SUB_PATH = 'Pictures'
DEFAULT_ALBUM_ART_SUB_SUB_PATH = 'AlbumArt'

SONG_FILE_EXT = '.flac'  # keep lower-case
SONG_SHADOW_FILE_EXT = '.json'  # keep lower-case

ALBUM_ART_JPG = '.jpg'  # keep lower-case
ALBUM_ART_PNG = '.png'  # keep lower-case
ALBUM_ART_EXT = [ALBUM_ART_JPG, ALBUM_ART_PNG]  # keep lower-case
MISSING_MARK_EXT = '.missing'
REVIEWED_MARK_EXT = '.reviewed'


def get_default_root():
    global DEFAULT_ROOT
    if not DEFAULT_ROOT:
        DEFAULT_ROOT = get_env_var('MUSIC')
        if not DEFAULT_ROOT:
            DEFAULT_ROOT = '{}/{}'.format(get_home(), DEFAULT_MUSIC_ROOT)
    return DEFAULT_ROOT


def get_default_album_art_root(dryrun=True, verbose=False):
    global DEFAULT_ALBUM_ART_ROOT, DEFAULT_ALBUM_ART_SUB_PATH
    global DEFAULT_ALBUM_ART_SUB_SUB_PATH
    if not DEFAULT_ALBUM_ART_ROOT:
        DEFAULT_ALBUM_ART_ROOT = get_env_var('ALBUM_ART')
        if not DEFAULT_ALBUM_ART_ROOT:
            DEFAULT_ALBUM_ART_ROOT = '{}/{}'.format(
                get_home(), DEFAULT_ALBUM_ART_SUB_PATH)
            make_dir(DEFAULT_ALBUM_ART_ROOT, DEFAULT_ALBUM_ART_SUB_SUB_PATH,
                     conditionally=True, dryrun=dryrun, verbose=verbose)
            DEFAULT_ALBUM_ART_ROOT += '/' + DEFAULT_ALBUM_ART_SUB_SUB_PATH
    return DEFAULT_ALBUM_ART_ROOT


def is_song_file(file_name, include_shadow_files=True):
    if include_shadow_files:
        return (file_name.lower().endswith(SONG_FILE_EXT) or
                file_name.lower().endswith(SONG_SHADOW_FILE_EXT))
    else:
        return file_name.lower().endswith(SONG_FILE_EXT)


def is_supported_file_ext(file_name, include_shadow_files=True):
    return (is_song_file(file_name, include_shadow_files) or
            file_name.endswith(ALBUM_ART_JPG) or
            file_name.endswith(ALBUM_ART_PNG) or
            file_name.endswith(MISSING_MARK_EXT) or
            file_name.endswith(REVIEWED_MARK_EXT))


def new_mark_file(f):
    new_file(f, '# DO NOT DELETE')


def process_songs_dir(root, dir_name, project_filter, artist_filter,
                      album_filter, trace=False):

    if trace:
        stdout('process_songs_dir', root, dir_name,
               project_filter, artist_filter, album_filter)

    root = assure_not_endswith(root, '/')
    assert_path_exists(root)

    if dir_name == root:
        return False, None, None, None
    else:
        unrooted = dir_name.replace(root + '/', '')
    if '/' not in unrooted or len(unrooted.split('/')) != 3:
        # need to be 3 levels deep
        return False, None, None, None

    # parse the 3 levels
    artist_album = unrooted.split('/')
    project = u(artist_album[0])
    artist = u(artist_album[1])
    album = u(artist_album[2])

    process = True
    if project_filter:
        process = filter_by(project, project_filter)
    if process and artist_filter:
        process = filter_by(artist, artist_filter)
    if process and album_filter:
        process = filter_by(album, album_filter)

    return process, project, artist, album


def get_missing_file_full_path(path, track):
    return path + '/.' + str(track) + '.missing'


def missing_file_exists(path, track):
    return is_file(get_missing_file_full_path(path, track))


def add_missing_file(path, track, dryrun=True):
    missed = get_missing_file_full_path(path, track)
    if dryrun:
        stdout('(dryrun)', missed, 'created')
    else:
        new_mark_file(missed)
        yellow(missed, 'created')


def get_filtered_songs(path, song_fs,
                       artist_filter=None, album_filter=None,
                       title_filter=None,
                       sort_per_track=False, post_process_songs=False,
                       print_header=True,
                       no_warn=False, deep_warn=False,
                       mark_missing_songs=False, dryrun=True,
                       verbose=False, silent=False, debug=False):
    printed_header = False
    filtered_songs = {}
    missed_songs = []
    warnings = 0
    max_track_len = 0
    total_album_tracks = None  # unknown or inconsistent
    track_info_per_song = {}

    for song in song_fs:
        if is_song_file(song):
            s = Song(path=path, song_f=song, debug=debug)
            if ((not artist_filter or
                 artist_filter.lower() in s.get('ALBUMARTIST').lower()) and
                    ((not album_filter or
                      album_filter.lower() in s.get('ALBUM').lower()) and
                     (not title_filter or
                      title_filter.lower() in s.get('TITLE').lower()))):
                if print_header and not printed_header:
                    green()
                    green('Listing', path)
                    printed_header = True
                if sort_per_track:
                    track_tag = s.get_track_nbr_as_string(verbose=verbose)
                    track_nbr, total = s.parse_track_nbr(track_tag)
                    track_info_per_song[s.name()] = (track_nbr, total)

                    # build up a list, in case of mixes directory, there would
                    # be track number overlaps
                    f_songs = filtered_songs.get(track_nbr)
                    if f_songs:
                        f_songs.append(s)
                    else:
                        filtered_songs[track_nbr] = [s]

                else:
                    track_tag = s.get_track_nbr_as_string(verbose=verbose)
                    filtered_songs[len(filtered_songs)] = [s]

                max_track_len = max(max_track_len, len(track_tag))

    if filtered_songs and sort_per_track and post_process_songs:
        prev_track_nbr = 0
        song_that_gave_total_tracks = None
        total_tracks_is_inconsistent = False
        for track_nbr in sorted(filtered_songs):
            first_song = True
            for song in filtered_songs[track_nbr]:
                song_f = song.name()
                song_base = song_f[:-len(SONG_FILE_EXT)]
                track_nbr, total = track_info_per_song[song_f]
                if missing_file_exists(path, track_nbr):
                    error('.missing file exists for', song_f, end='\n')
                    error('You must delete it:',
                          get_missing_file_full_path(path, track_nbr),
                          end='\n')
                if first_song:
                    if track_nbr != prev_track_nbr + 1:
                        # TODO(if last song is missing, we don't report)
                        for i in range(prev_track_nbr + 1, track_nbr):
                            if not missing_file_exists(path, i):
                                if mark_missing_songs:
                                    add_missing_file(path, i, dryrun)
                                else:
                                    missed_songs.append((path, i))

                    prev_track_nbr = track_nbr
                    first_song = False

                if total and not total_tracks_is_inconsistent:
                    if total_album_tracks is None:
                        total_album_tracks = total
                        song_that_gave_total_tracks = song_base
                    elif total_album_tracks != total:
                        total_tracks_is_inconsistent = True
                        total_album_tracks = None

                        if not no_warn:
                            warn('Within', path, 'album,')
                            yellow('     ', song_base,
                                   'has inconsistent total tracks with',
                                   song_that_gave_total_tracks)
                            if deep_warn:
                                print_songs(path, song_fs,
                                            artist_filter, album_filter,
                                            title_filter, sort_per_track=True,
                                            verbose=verbose, silent=silent,
                                            debug=debug)
                            warnings += 1

        if not silent:
            for song in missed_songs:
                warn(song[0], '[Track', song[1], '\b] is missing')
                warnings += 1

    return (filtered_songs, missed_songs, total_album_tracks, warnings,
            max_track_len)


def print_songs(path, songs,
                artist_filter=None, album_filter=None, title_filter=None,
                detailed=False, extended=False,
                header=False,  # TODO(fill in correctly)
                sort_per_track=False, warn_for_inconsistencies=False,
                print_paths=False, path_only=False,
                dos_format=False, windows_format=False,
                verbose=False, silent=False, debug=False):

    printed = warnings = 0
    filtered_songs, missed_songs, _, _, max_track_len = get_filtered_songs(
        path, songs,
        artist_filter, album_filter, title_filter,
        sort_per_track=sort_per_track, print_header=not silent,
        post_process_songs=warn_for_inconsistencies,
        verbose=verbose, silent=silent, debug=debug)

    def print_song(p_song):
        track_tag = p_song.get('TRACKNUMBER')
        # library will cut leading spaces if you don't add a string part
        p_song.set('TRACKNUMBER', 'T' + track_tag.rjust(max_track_len))
        start_bold()
        if print_paths:
            print_path(p_song.full_path(), dos_format, windows_format)
        end_color()
        if not path_only:
            p_song.print_tags(detailed=detailed, extended=extended,
                              header=header, highlight_title=not print_paths)

    if sort_per_track:
        for track_nbr in sorted(filtered_songs):
            for song in filtered_songs[track_nbr]:
                print_song(song)
                printed += 1
    else:
        for songs in filtered_songs.values():
            for song in songs:  # there will, as no sorting was done, be only 1
                #                 in the list, but for readability
                print_song(song)
                printed += 1

    return printed, warnings



