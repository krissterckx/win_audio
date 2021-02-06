import argparse
import os
from string import ascii_letters

from __lib.base import stdout, green, yellow, cyan, warn, a_else_b, now, u, \
    mark_dry_or_production_run, path_exists, rename_dir, merge_dir, \
    rename_file, is_py2, get_env_var, error, fatal_error, end_color, \
    ConsoleColors, print_paths, assert_non_empty_dir, is_windows
from __lib.extd_base import to_camel_case
from __lib.functions import SONG_FILE_EXT, get_default_root, process_songs_dir
from __lib.song import Song

FIX_ARTIST_DIRS = {
    # 'Grease (The Motion Picture)':
    #     'Grease (The Original Soundtrack From The Motion Picture)',
}

FIX_ARTIST_TAGS = {
    # 'Nederlandstalige New Wave': 'New Wave - Nederlandstalig',
}

FIX_ALBUM_TAGS = {
    # 'Speakerboxxx/The Love Below': 'Speakerboxxx - The Love Below',
    # 'Succes/Ik Ben Twan': 'Succes - Ik Ben Twan'
}

COLLECTION_ALBUMS = {
    # -- the keys identify Collection albums;                         --
    # -- fill in value if want to overwrite the Collection album name --
    #
    # '10 Years Armada': None
}

FIXED_SONGS_REPORT = '/tmp/fixed_songs' + '_' + now()

errors_fixed = 0
errors_unresolved = 0
sung_it = False

JOKER_VALUE = 'Various'

TOLERATED_CHARS_IN_TAGS_REPLACED_TO_IN_FILESYSTEM = {
    # Cygwin is not the problem here - the problem is Windows Explorer
    '"': "''",
    '/': '-',
    ':': '-',
    '*': '+',
    '?': ''
}
REPLACE_CHARS = {
    '  ': ' '
}
REPLACE_CHARS_IN_TAGS_ONLY = {  # meant to fix earlier corrections only
    "''": '"'  # ('' to ")        -- can eventually go --
}
REPLACE_CHARS_IN_ARTISTS_ONLY = {
    ',': ''  # can't have comma's in artist name, as we split by comma
}
PRESERVED_NAMES = ['deadmau5']   # Mind! Can be single word only!

fixed_songs = []


def audit_song(root, project, artist_d, album_d, song_f,
               reset_artist_ref, reset_album_ref,
               dir_structure_as_ref=False,
               set_artist=None, set_album=None, set_song=None,
               force_write=False,
               dryrun=True, verbose=False, silent=False, debug=False):
    global errors_fixed, errors_unresolved, sung_it

    def debug_out(*args, **kwargs):
        if debug:
            end_color()
            stdout(*args, **kwargs)

    debug_out('audit_song:', root, project, artist_d, album_d, song_f)

    song = Song(root, project, artist_d, album_d, song_f=song_f, debug=debug)

    title_f = song_f[:-len(SONG_FILE_EXT)]
    pre_errors_fixed = errors_fixed

    keep = {}
    init_the_song = '*** UNINITIALIZED ***'
    sung_it = False

    def keep_it():
        for _tag in ('TITLE', 'ALBUM', 'ARTIST', 'ALBUMARTIST'):
            keep[_tag] = song.get(_tag)

    def force_it():
        keep['TITLE'] = ''
        sing_it()
        cyan('FORCE-WRITING TITLE ', end='')

    def save_it():
        song.save(dryrun)

    def print_it(p_tags=None, offset=4):
        p_tags = p_tags or song.get_tags()
        for _tag in Song.get_tag_keys():
            if _tag == 'TRACKNUMBER':
                continue  # skip
            stdout(' ' * offset + _tag + ': \'' + p_tags[_tag] + '\'')

    def sing_it(force=False):
        global sung_it  # python 3 can do nonlocal but in py2 is readonly
        elaborated = False
        if not silent and (force or not sung_it):
            if elaborated:
                stdout(init_the_song, end='')  # sing it
            else:
                yellow('Fixing', project, '/', artist_d, '/', album_d, '/',
                       song_f)
            sung_it = True

    def did_it():
        for _tag in ('TITLE', 'ALBUM', 'ARTIST', 'ALBUMARTIST'):
            if song.get(_tag) != keep[_tag]:
                return True
        return False

    def report(*args, **kwargs):
        if not silent:
            cyan(*args, **kwargs)

    def replace_name(name):
        set_name = None
        suffix = None

        if name.endswith('-'):  # -X- assumed
            for i in range(999):
                s = ' -{}-'.format(i)
                if name.endswith(s):
                    suffix = s
                    truncated_name = name[:-len(s)]
                    debug_out('Checking', truncated_name, 'instead of', name)
                    name = truncated_name
                    break

        e = to_camel_case(name, PRESERVED_NAMES)
        if e != name:
            set_name = e
            name = set_name

        done = False
        while not done:
            done = True
            for c in (' ', ',', ';', ':', '&'):
                while name.endswith(c):
                    set_name = name[:-1]
                    done = False
                    name = set_name

        if name == '?':
            set_name = 'Q'
        else:
            prev_name = name
            for c in REPLACE_CHARS:
                name = name.replace(c, REPLACE_CHARS[c])
            if name != prev_name:
                set_name = name

        if set_name and suffix:
            set_name += suffix

        if set_name:
            debug_out('replace_name: replaced', name, 'to', set_name)

        return set_name

    def fix_dir_name(name):
        if name.endswith('.'):
            # WINDOWS DOESN'T DEAL WITH DOTS AT END OF A DIRECTORY...
            name = name[:-1] + '. ()'
        return name

    def tag_to_filesystem_name(name, is_dir):
        if is_dir:
            name = fix_dir_name(name)
        for c in TOLERATED_CHARS_IN_TAGS_REPLACED_TO_IN_FILESYSTEM:
            name = name.replace(
                c, TOLERATED_CHARS_IN_TAGS_REPLACED_TO_IN_FILESYSTEM[c])
        for c in ascii_letters:
            name = name.replace(c + '- ', c + ' - ')
        return name

    def fix_artist_tag():
        artist = song.get('ALBUMARTIST')
        t = FIX_ARTIST_TAGS.get(artist)
        if t:
            sing_it()
            report('FIXING ARTIST ', end='')
            song.set('ALBUMARTIST', t)
            return t
        else:
            return None

    def fix_artist_dir():
        d = FIX_ARTIST_DIRS.get(artist_d)
        if d:
            sing_it()
            report('FIX_ARTIST_DIR [Renaming dir', artist_d, 'to', d + ']')
            # mind, actual rename is not done here!
            return d
        return None

    def fix_album_tag():
        album = song.get('ALBUM')
        t = FIX_ALBUM_TAGS.get(album)
        if t:
            sing_it()
            report('FIXING ALBUM ', end='')
            song.set('ALBUM', t)
            return t
        else:
            return None

    def fix_tags_for_camel_case_and_more():
        for tag in ('TITLE', 'ALBUM', 'ARTIST', 'ALBUMARTIST'):
            t_tag = song.get(tag)

            debug_out('Processing', tag, '=', t_tag)

            if t_tag:
                new_tag = replace_name(t_tag)

                # replace comma's in artist
                if tag == 'ALBUMARTIST':
                    t_cur = new_tag if new_tag else t_tag
                    t_new = t_cur
                    for c in REPLACE_CHARS_IN_ARTISTS_ONLY:
                        t_new = t_new.replace(
                            c, REPLACE_CHARS_IN_ARTISTS_ONLY[c])
                    if t_new != t_cur:
                        new_tag = t_new
                        sing_it()
                        report('FIXING ALBUMARTIST [' + new_tag + '] ', end='')
                        song.set(tag, new_tag, straight_overwrite_artist=True)

                # extra logic (eventually can go)
                def retag(name):
                    for r in REPLACE_CHARS_IN_TAGS_ONLY:
                        name = name.replace(r, REPLACE_CHARS_IN_TAGS_ONLY[r])
                    return name

                if new_tag:
                    new_tag = retag(new_tag)
                else:
                    old_t = t_tag
                    t_tag = retag(t_tag)
                    if t_tag != old_t:
                        new_tag = t_tag
                # end of extra logic (eventually can go)

                if new_tag:
                    sing_it()
                    report('FIXING NAME [' + new_tag + '] ', end='')
                    song.set(tag, new_tag)

    def fix_dirs_for_camel_case_and_more():
        debug_out('fix_dirs_for_camel_case_and_more')

        return (replace_name(set_artist if set_artist else artist_d),
                replace_name(set_album if set_album else album_d),
                replace_name(set_song if set_song else title_f))

    def fix_collection_albums():
        debug_out('fix_collection_albums')

        if song.get('ALBUM') in COLLECTION_ALBUMS:
            album_t = song.get('ALBUM')
            overwrite = u(a_else_b(
                COLLECTION_ALBUMS[album_t], album_t))

            if song.get('ALBUMARTIST') != overwrite:
                sing_it()
                report('COLLECTION:RENAMING ', end='')
                song.set('ALBUM', overwrite)
                song.set('ALBUMARTIST', overwrite)

            if overwrite not in song.get('ARTIST'):
                sing_it()
                if song.get('ARTIST').endswith(keep['ALBUM']):
                    report('COLLECTION:STRIPPING ', end='')
                    song.set('ARTIST',
                             song.get('ARTIST')[:-(len(keep['ALBUM']) + 2)])
                song.set('ARTIST', song.get('ARTIST') + ', ' + overwrite)
                report('COLLECTION:MARKING ', end='')

    def truncate_artists():
        while True:
            song_artist = song.get('ALBUMARTIST')
            artist = song.get('ARTIST')
            if song_artist:
                if ',' in song_artist:
                    sing_it()
                    report('TRUNCATING ALBUMARTIST', end='')
                    song.set('ALBUMARTIST',
                             song.get('ALBUMARTIST').split(',')[0])

                if song.get('ALBUMARTIST') not in song.get('ARTIST'):
                    song.set('ARTIST',
                             song.get('ARTIST') + ', ' +
                             song.get('ALBUMARTIST'))
                break

            elif artist:
                sing_it()
                report('FIXING ALBUMARTIST ', end='')
                if ',' in artist:
                    song.set('ALBUMARTIST', song.get('ARTIST').split(',')[0])
                else:
                    song.set('ALBUMARTIST', song.get('ARTIST'))

            else:
                error('No ARTIST and no ALBUMARTIST?')
                error(project, '/', artist_d, '/', album_d, '/', song_f, '\n')
                break

    def finish_it():
        global errors_fixed

        debug_out('finish_it')

        artist = song.get('ALBUMARTIST')
        contributing_artists = song.get('ARTIST')
        album = song.get('ALBUM')
        title = song.get('TITLE')

        if sung_it:
            report('OK')
        if did_it():
            if silent:
                green('Retagged', project, '/', artist,
                      '(' + contributing_artists + ') /', album, '/', title)
            else:
                stdout('WAS:')
                print_it(keep)
                stdout('BECAME:')
                print_it()
            save_it()  # this is the moment where we save!
            errors_fixed += 1

    def audit_entity(entity_tag, unrooted_entity_path_root,
                     is_file, file_extension,
                     entity_d, entity, set_entity):
        global errors_fixed, errors_unresolved

        debug_out('audit_entity:', entity_tag, unrooted_entity_path_root,
                  is_file, file_extension, entity_d, entity, set_entity)

        def retag(to):
            green('Retagging',
                  unrooted_entity_path_root.replace('/', ' / '), '/',
                  entity, 'to', to)
            # TODO(do we need to save here?)
            song.set(entity_tag, to, save=True, dryrun=dryrun)

        def rename(to):
            rooted_entity_path_root = root + '/' + unrooted_entity_path_root
            if is_file:
                green('Renaming',
                      unrooted_entity_path_root.replace('/', ' / '), '/',
                      entity_d + file_extension, 'to',
                      to + file_extension)
                rename_file(rooted_entity_path_root,
                            entity_d + file_extension,
                            to + file_extension,
                            safe_rename=True, add_suffix_if_exists=True,
                            dryrun=dryrun, verbose=verbose,
                            silent=silent, debug=debug)
            elif (path_exists(rooted_entity_path_root + '/' + to) and
                    not (is_windows() and entity_d.lower() == to.lower())):
                green('Merging', unrooted_entity_path_root, '/',
                      entity_d, 'into', to)
                merge_dir(rooted_entity_path_root + '/' + entity_d,
                          rooted_entity_path_root + '/' + to,
                          safe_merge=True, add_suffix_if_exists=True,
                          merge_subdirs=True,
                          dryrun=dryrun, verbose=verbose, silent=silent,
                          debug=debug)
            else:
                green('Renaming',
                      unrooted_entity_path_root.replace('/', ' / '), '/',
                      entity_d, 'to', to)
                rename_dir(rooted_entity_path_root, entity_d, to,
                           safe_rename=False, dryrun=dryrun,
                           verbose=verbose, silent=silent, debug=debug)

        if set_entity:
            debug_out('audit_entity:', entity_tag, 'set to', set_entity)
            modified = False
            if entity != set_entity:
                sing_it()
                retag(set_entity)
                errors_fixed += 1
                modified = True
            c_set_entity = tag_to_filesystem_name(set_entity, not is_file)
            if entity_d != c_set_entity:
                sing_it()
                rename(c_set_entity)
                errors_fixed += 1
                modified = True
            return c_set_entity if modified else None

        else:
            c_entity = tag_to_filesystem_name(entity, not is_file)
            if c_entity != entity_d and entity_d != JOKER_VALUE:
                if dir_structure_as_ref:
                    sing_it()
                    retag(entity_d)
                    errors_fixed += 1
                    return entity_d
                else:
                    sing_it()
                    rename(c_entity)
                    errors_fixed += 1
                    return c_entity

    def audit_artist(set_it):
        artist = song.get('ALBUMARTIST')
        return audit_entity('ALBUMARTIST', project, False, None,
                            artist_d, artist, set_it)

    def audit_album(set_it):
        album = song.get('ALBUM')
        return audit_entity('ALBUM', project + '/' + artist_d, False, None,
                            album_d, album, set_it)

    def audit_title(set_it):
        title = song.get('TITLE')
        return audit_entity('TITLE', project + '/' + artist_d + '/' + album_d,
                            True, SONG_FILE_EXT, title_f, title, set_it)

    orig_artist_d = artist_d
    orig_album_d = album_d
    orig_title_d = title_f

    if dir_structure_as_ref:
        artist_mod = fix_artist_dir()
        if artist_mod:
            set_artist = set_artist or artist_mod
            if not dryrun:
                cyan('(Resetting ARTIST)')
                reset_artist_ref[0] = set_artist

        artist_mod, album_mod, title_mod = fix_dirs_for_camel_case_and_more()

        if artist_mod:
            set_artist = set_artist or artist_mod  # mind, despite efforts to
            #                                        correct it, when was pre-
            #                                        set, we stick to what was
            #                                        set (manually or via
            #                                             fix_artist_dir)
            if not dryrun and not reset_artist_ref[0]:
                cyan('(Resetting ARTIST)')
                reset_artist_ref[0] = set_artist

        if album_mod:
            set_album = set_album or album_mod  # mind, same here, but then
            #                                     only for previously manually
            #                                     set in this case
            if not dryrun:
                cyan('(Resetting ALBUM)')
                reset_album_ref[0] = set_album

        if title_mod:
            set_song = set_song or title_mod

    else:
        keep_it()
        if force_write:
            force_it()
        fix_artist_tag()
        fix_album_tag()
        fix_tags_for_camel_case_and_more()
        fix_collection_albums()
        truncate_artists()
        finish_it()

    modified_to = audit_artist(set_artist)
    if modified_to and not dir_structure_as_ref:
        artist_d = modified_to
        if not dryrun:
            cyan('(Resetting ARTIST)')
            reset_artist_ref[0] = modified_to
    artist_d = fix_dir_name(artist_d)  # always

    modified_to = audit_album(set_album)
    if modified_to and not dir_structure_as_ref:
        album_d = modified_to
        if not dryrun:
            cyan('(Resetting ALBUM)')
            reset_album_ref[0] = modified_to
    album_d = fix_dir_name(album_d)  # always

    modified_to = audit_title(set_song)
    if modified_to and not dir_structure_as_ref:
        title_f = modified_to

    number_modified = errors_fixed > pre_errors_fixed
    if number_modified:
        fixed_songs.append(
            root + '/' + project + '/' +
            # if dryrun, files aren't actually changed
            (orig_artist_d if dryrun else artist_d) + '/' +
            (orig_album_d if dryrun else album_d) + '/' +
            (orig_title_d if dryrun else title_f) + SONG_FILE_EXT
        )
    return number_modified


def main():
    if is_py2():
        warn('Running as python 3 is advised')
        stdout()

    program = 'audit_songs'
    description = '''
    Audits songs or list of songs with its directory structure
    '''

    parser = argparse.ArgumentParser(prog=program,
                                     description=description)
    parser.add_argument('-p', '--production', help='Enable production run',
                        action='store_true')
    parser.add_argument('-j', '--project-filter', type=str,
                        help='Set project filter')
    parser.add_argument('-a', '--artist-filter', type=str,
                        help='Set artist filter')
    parser.add_argument('-b', '--album-filter', type=str,
                        help='Set album filter')
    parser.add_argument('-c', '-t', '--title-filter', type=str,
                        help='Set title filter')
    parser.add_argument('--dir-structure-as-ref',
                        help=('Set the dir structure as the reference, '
                              'opposed to the default\'s song tags'),
                        action='store_true')
    parser.add_argument('--set-artist', type=str,
                        help='Set (overrules) artists. Always use with '
                             '--artist-filter')
    parser.add_argument('--set-album', type=str,
                        help='Set (overrules) album. Always use with '
                             '--album-filter')
    parser.add_argument('--set-song', type=str,
                        help='Set (overrules) song title, Always use with '
                             '--title-filter')
    parser.add_argument('--provide-report',
                        help='Provide a report of modified songs',
                        action='store_true')
    parser.add_argument('-x', '--path', type=str, help='Sets root path')
    parser.add_argument('-n', '--limit-changes', type=int,
                        help='Set a limit to amount of changes')
    parser.add_argument('-v', '--verbose', help='Enable verbosity',
                        action='store_true')
    parser.add_argument('-s', '--silent', help='Enable silence',
                        action='store_true')
    parser.add_argument('-d', '--debug', help='Enable debug',
                        action='store_true')
    parser.add_argument('--force-write', help='Force-Write',
                        action='store_true')

    args = parser.parse_args()
    root = args.path or get_default_root()
    dryrun = not args.production or get_env_var('DRYRUN')
    silent = args.silent or get_env_var('SILENT')
    debug = args.debug or get_env_var('DEBUG')
    verbose = args.verbose or get_env_var('VERBOSE') or debug
    provide_report = args.provide_report
    project_filter = args.project_filter
    artist_filter = args.artist_filter
    album_filter = args.album_filter
    title_filter = args.title_filter
    dir_structure_as_ref = args.dir_structure_as_ref
    set_artist = args.set_artist
    set_album = args.set_album
    set_song = args.set_song
    limit_changes = args.limit_changes or 9999999999

    if set_artist and not artist_filter:
        fatal_error('Must set artist filter when setting artist')
    if set_album and not album_filter:
        fatal_error('Must set album filter when setting album')
    if set_song and not title_filter:
        fatal_error('Must set title filter when setting song title')

    if title_filter and title_filter.lower().endswith(SONG_FILE_EXT):
        title_filter = title_filter[:-len(SONG_FILE_EXT)]
    if set_song and set_song.lower().endswith(SONG_FILE_EXT):
        set_song = set_song[:-len(SONG_FILE_EXT)]

    assert_non_empty_dir(root)
    mark_dry_or_production_run(dryrun)

    for dir_name, _, filenames in os.walk(root):
        process, project, artist, album = process_songs_dir(
            root, dir_name, project_filter, artist_filter, album_filter)
        if not process:
            continue

        if not title_filter and verbose:
            yellow('Processing', project, artist, album)

        for song in filenames:
            if not song.lower().endswith(SONG_FILE_EXT):
                continue
            if title_filter:
                if title_filter.lower() != song[:-len(SONG_FILE_EXT)].lower():
                    continue
                elif verbose:
                    yellow('Processing', project, artist, album, song)
            elif debug:
                yellow('Processing', project, artist, album, song)

            reset_artist = [None]
            reset_album = [None]

            if audit_song(
                    root, project, artist, album, song,
                    reset_artist, reset_album,
                    dir_structure_as_ref=dir_structure_as_ref,
                    # Once a first song in album fixes the artist, same artist
                    # is dictated to rest of songs. This avoids ping-pong'ing.
                    set_artist=set_artist if set_artist else None,
                    # Once a first song in album fixes the album, same album is
                    # dictated to rest of songs. This avoids ping-pong'ing.
                    set_album=set_album if set_album else None,
                    # User specified song
                    set_song=set_song,
                    force_write=args.force_write, dryrun=dryrun,
                    verbose=verbose, silent=silent, debug=debug):
                if debug:
                    stdout(errors_fixed, 'errors fixed')
                if reset_artist[0]:
                    if (artist_filter and
                            artist.lower() == artist_filter.lower()):
                        artist_filter = reset_artist[0]
                    artist = reset_artist[0]  # Make sure next songs in album
                    #                           will load correctly
                if reset_album[0]:
                    if (album_filter and
                            album.lower() == album_filter.lower()):
                        album_filter = reset_album[0]
                    album = reset_album[0]  # Make sure next songs in album
                    #                         will load correctly
                if not silent:
                    stdout()

            if errors_fixed >= limit_changes:
                break

    if not silent and errors_fixed >= limit_changes:
        stdout()
    stdout(errors_fixed, 'errors were fixed;',
           errors_unresolved, 'remaining errors found')

    if provide_report and fixed_songs:
        stdout('Generating reports', ConsoleColors.ALERT)

        print_paths(fixed_songs,
                    write_to_file=FIXED_SONGS_REPORT + '.cyg')
        print_paths(fixed_songs, dos_format=True,
                    write_to_file=FIXED_SONGS_REPORT + '.dos')

        stdout(ConsoleColors.ENDC + 'Check the report:')
        stdout('   ', 'cat', FIXED_SONGS_REPORT + '.cyg')
        stdout('   ', 'cat', FIXED_SONGS_REPORT + '.dos')
        stdout()
        stdout('Feed into foobar2000 as:')
        stdout('    for i in $(cat ' + FIXED_SONGS_REPORT +
               '.dos); do songs="$songs $i"; done; foobar2000.exe /add $songs')
        stdout()
        stdout('Or do a little test:')
        stdout('    for i in $(cat ' + FIXED_SONGS_REPORT +
               '.dos); do echo "$i"; done')
        stdout()


if __name__ == "__main__":
    main()
