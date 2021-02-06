import argparse
import os

from __lib.base import stdout, yellow, cyan, u, assert_non_empty_dir, \
    numerical_input, string_input, start_cyan, end_color, is_file, \
    rename_file, end, get_env_var
from __lib.functions import SONG_FILE_EXT, get_default_root, \
    process_songs_dir, get_filtered_songs, new_mark_file, add_missing_file
from __lib.song import Song


def option(n, s):
    if 0 <= n <= 9:
        stdout(' [' + str(n) + ']', s)
    else:
        stdout('[' + str(n) + ']', s)


def edit_song(song, debug=False):
    FILL_UP_TO = 15

    done = False
    while not done:
        start_cyan()
        option(0, 'None')
        option(1, 'SONG FILE'.ljust(FILL_UP_TO) + song.name())
        idx = 2
        tag_qualifiers = Song.get_tag_keys()
        for tag in tag_qualifiers:
            option(idx, tag.ljust(FILL_UP_TO) + song.get(tag))
            idx += 1
        end_color()
        stdout()

        while True:
            t = numerical_input('Edit file/tag', 0, idx - 1)
            if t == 0:  # exit
                done = True
                break
            elif t == 1:  # new song file
                f = string_input('New SONG FILE', prefill=song.name())
                yellow('Updating SONG FILE to', f)
                rename_file(song.path(), song.name(), f,
                            dryrun=False, silent=True, debug=debug)
                song = Song(path=song.path(), song_f=f, debug=debug)
                stdout()
            else:
                t = tag_qualifiers[t - 2]
                f = string_input('New ' + t, prefill=song.get(t))
                yellow('Updating', t, 'to', f)
                song.set(t, f, save=True, dryrun=False)  # modify for real!
                stdout()

    return song


def review_songs(path, song_files, title_filter,
                 detailed=True, sort=True,
                 verbose=False, silent=False, radio_silent=False, debug=False):
    songs = []

    filtered_songs, missed_songs, _, _, _ = get_filtered_songs(
        path, song_files, title_filter=title_filter,
        sort_per_track=sort, post_process_songs=sort,
        print_header=not silent,
        verbose=verbose, silent=silent, no_warn=radio_silent, debug=debug)

    if not filtered_songs:
        return

    for track_nbr in sorted(filtered_songs):
        for song in filtered_songs[track_nbr]:
            songs.append(song)

    PAGE_SIZE = 20
    done = False
    idx = 1

    def option_title(title_idx):
        s = songs[title_idx - 1]
        # noinspection PyTypeChecker
        title = s.get('TITLE')
        if detailed:
            # noinspection PyTypeChecker
            track_nr = s.get('TRACKNUMBER')
            title += (' (' + track_nr + ')')
        option(title_idx, title)

    while not done:
        if idx > len(songs):
            break

        default = idx - 1
        stdout()
        option(default, 'None')

        for _ in range(PAGE_SIZE):
            if idx > len(songs):
                done = True
                break
            option_title(idx)
            idx += 1

        def add_options(_idx):
            _add_tags = None

            def _add_option(_s, _i):
                option(_i, _s)
                return _i, _i + 1

            if missed_songs:
                _add_tags, _idx = _add_option('-- ADD .missing TAGS --', _idx)
            _reload, _idx = _add_option('-- RELOAD --', _idx)
            _exit_the_game, _idx = _add_option('-- EXIT --', _idx)

            return _add_tags, _reload, _exit_the_game

        add_tags, reload, exit_the_game = add_options(idx)
        stdout()

        while True:
            c = numerical_input('Song to edit', default, exit_the_game)
            if missed_songs and c == add_tags:
                stdout()
                for missed in missed_songs:
                    add_missing_file(missed[0], missed[1], dryrun=False)
                stdout()
                c = None

            elif c == reload:
                stdout()
                option(default, 'None')
                for i in range(default + 2, idx):
                    option_title(i)
                add_options(idx)
                cyan('(mind, not re-sorted)')
                cyan()
                c = None

            elif c == exit_the_game:
                cyan('Bye.')
                end()

            elif c == default:
                break

            if c is not None:
                stdout()
                song_idx = c - 1
                songs[song_idx] = edit_song(songs[song_idx], debug=debug)


def main():
    program = 'review_songs'
    description = '''
    Review songs based on user input
    '''

    parser = argparse.ArgumentParser(prog=program,
                                     description=description)
    parser.add_argument('-j', '--project-filter', type=str,
                        help='Set project filter')
    parser.add_argument('-a', '--artist-filter', type=str,
                        help='Set artist filter')
    parser.add_argument('-b', '--album-filter', type=str,
                        help='Set album filter')
    parser.add_argument('-c', '-t', '--title-filter', type=str,
                        help='Set title filter')
    parser.add_argument('-x', '--path', type=str, help='Sets root path')
    parser.add_argument('-r', '--review-stamps',
                        help='Create/Use review stamps', action='store_true')
    parser.add_argument('-v', '--verbose',
                        help='Enable verbose', action='store_true')
    parser.add_argument('-s', '--silent',
                        help='Enable silence', action='store_true')
    parser.add_argument('-rs', '--radio-silent', help='Enable radio silence',
                        action='store_true')
    parser.add_argument('-d', '--debug',
                        help='Enable debug', action='store_true')

    args = parser.parse_args()
    root = args.path or get_default_root()
    radio_silent = args.radio_silent or get_env_var('RADIO_SILENT')
    silent = args.silent or get_env_var('SILENT') or radio_silent
    debug = args.debug or get_env_var('DEBUG')
    verbose = args.verbose or get_env_var('VERBOSE') or debug

    assert_non_empty_dir(root)

    project_filter = args.project_filter
    artist_filter = args.artist_filter
    album_filter = args.album_filter
    title_filter = args.title_filter
    review_stamps = args.review_stamps

    if title_filter and title_filter.lower().endswith(SONG_FILE_EXT):
        title_filter = title_filter[:-len(SONG_FILE_EXT)]

    for dir_name, _, song_fs in os.walk(root):
        # gotcha... this doesn't work if i specify a full detailed path, up
        # to the album dir ...
        process, project, artist, album = process_songs_dir(
            root, dir_name, project_filter, artist_filter, album_filter)

        if process:
            path = root + '/' + project + '/' + artist + '/' + album
            reviewed_mark = path + '/.reviewed'
            if review_stamps and is_file(reviewed_mark):
                if debug:
                    cyan('Skipping', project, '/', artist, '/', album)
            else:
                review_songs(path, song_fs, title_filter,
                             verbose=verbose, silent=silent,
                             radio_silent=radio_silent,
                             debug=debug)
                if review_stamps:
                    new_mark_file(reviewed_mark)


if __name__ == "__main__":
    main()
