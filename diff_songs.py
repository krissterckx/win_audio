import argparse
import os

from __lib.base import stdout, green, red, warn, ConsoleColors, \
    mark_dry_or_production_run, make_dir, remove_dir, remove_file, copy_file, \
    fatal_error, get_env_var
from __lib.functions import SONG_FILE_EXT, is_supported_file_ext, \
    process_songs_dir
from __lib.song import Song

PROCESSING = 'Processing:  '


def diff_tags(f1, f2, name1=None, name2=None,
              print_all_diffs=False, extended=True,
              print_on_diff=True, print_on_diff_f=None, debug=False):
    s1 = Song(song_f=f1, debug=debug)
    s2 = Song(song_f=f2, debug=debug)

    return s1.diff(s2, my_name=name1, other_name=name2,
                   print_all_diffs=print_all_diffs, extended=extended,
                   print_on_diff=print_on_diff,
                   print_on_diff_f=print_on_diff_f, debug=debug)


def diff_files(root1, root2, name1, name2,
               ignore_files_only_dirs=False,
               ignore_not_existing=False, ignore_file_differences=True,
               extended=False, synchronize=False,
               delete_root1_files_only=False,
               project_filter=None,
               artist_filter=None,
               album_filter=None,
               title_filter=None,
               dryrun=True, verbose=False, minimal_verbose=False, debug=False):
    diff_cnt = 0

    # --- minimal verbose: start ---
    index_c = '('  # always diff
    minimal_verbose_diff_cnt = -1
    # ---- minimal verbose: end ----

    for dir_name, _, file_names in os.walk(root1):
        process, project, artist, album = process_songs_dir(
            root1, dir_name, project_filter, artist_filter, album_filter)
        if not process:
            continue
        elif verbose:
            green('Processing', project, artist, album)

        # if dir_name == root1:
        #   continue

        unrooted = dir_name.replace(root1 + '/', '')
        target_dir_name = dir_name.replace(root1, root2)

        if minimal_verbose:
            if '/' not in unrooted:
                cur_index_c = unrooted[0:1].upper()
                if cur_index_c != index_c:
                    if minimal_verbose_diff_cnt != diff_cnt:
                        stdout(PROCESSING, end='')
                        minimal_verbose_diff_cnt = diff_cnt
                    stdout('\b' + cur_index_c, end='')
                    index_c = cur_index_c

        if not os.path.exists(target_dir_name) and not ignore_not_existing:
            if synchronize:
                if delete_root1_files_only:
                    remove_dir(root1, unrooted, dryrun=dryrun, verbose=True)
                else:
                    make_dir(root2, unrooted, dryrun=dryrun, verbose=True)
            else:
                if minimal_verbose:
                    stdout('\b' * len(PROCESSING), end='')
                red(target_dir_name, 'does not exist')

        if ignore_files_only_dirs:
            continue

        for file_name in file_names:

            if is_supported_file_ext(file_name, include_shadow_files=False):

                if title_filter and title_filter.lower() != file_name.lower():
                    continue
                elif verbose:
                    green('Processing', file_name)

                base_file = dir_name + '/' + file_name
                target_file = target_dir_name + '/' + file_name
                if os.path.exists(target_file):
                    if ignore_file_differences:
                        continue

                    action = (ConsoleColors.WARNING +
                              'DIFF .../{}/{}'.format(unrooted, file_name) +
                              ConsoleColors.ENDC)
                    if (extended and file_name.endswith(SONG_FILE_EXT) and
                            diff_tags(
                                base_file, target_file, name1, name2,
                                print_all_diffs=not synchronize,
                                print_on_diff_f=(
                                        ('\n' if minimal_verbose else '') +
                                        action +
                                        ConsoleColors.ALERT + ' DIFF' +
                                        ConsoleColors.ENDC
                                ) if synchronize else None,
                                debug=debug)):

                        diff_cnt += 1

                        if synchronize:
                            copy_file(
                                root1 + '/' + unrooted + '/' + file_name,
                                root2 + '/' + unrooted + '/' + file_name,
                                safe_copy=False,
                                dryrun=dryrun, verbose=True, debug=debug)

                    elif verbose:
                        stdout(action, end='')
                        green(' OK')

                elif not ignore_not_existing:
                    if synchronize:
                        if delete_root1_files_only:
                            remove_file(root1 + '/' + unrooted, file_name,
                                        safe_remove=False,
                                        dryrun=dryrun, verbose=verbose,
                                        debug=debug)
                        else:
                            copy_file(root1 + '/' + unrooted + '/' + file_name,
                                      root2 + '/' + unrooted + '/' + file_name,
                                      safe_copy=False,
                                      dryrun=dryrun, verbose=True, debug=debug)
                    else:
                        if minimal_verbose:
                            stdout('\b' * len(PROCESSING), end='')
                        red(target_file, 'does not exist')

                    diff_cnt += 1

            elif verbose:
                warn(file_name, 'is ignored in diff!')

    return diff_cnt


def main():
    program = 'diff_songs'
    description = '''
    Diffs songs'''

    parser = argparse.ArgumentParser(prog=program,
                                     description=description)
    parser.add_argument('-p', '--production',
                        help='Enable production run', action='store_true')
    parser.add_argument('-j', '--project-filter', type=str,
                        help='Set project filter')
    parser.add_argument('-a', '--artist-filter', type=str,
                        help='Set artist filter')
    parser.add_argument('-b', '--album-filter', type=str,
                        help='Set album filter')
    parser.add_argument('-c', '-t', '--title-filter', type=str,
                        help='Set title filter')
    parser.add_argument('-x1', '--path1', type=str,
                        help='Path to music file 1 or dir 1 of music files')
    parser.add_argument('-x2', '--path2', type=str,
                        help='Path to music file 2 or dir 2 of music files')
    parser.add_argument('-n1', '--name1', type=str,
                        help='A name for music file 1 or dir 1 of music files')
    parser.add_argument('-n2', '--name2', type=str,
                        help='A name for music file 2 or dir 2 of music files')
    parser.add_argument('-r', '--recursive',
                        help='Treat paths recursively', action='store_true')
    parser.add_argument('-e', '--extended',
                        help='Comparing also the song tags',
                        action='store_true')
    parser.add_argument('-v', '--verbose',
                        help='Enable verbosity', action='store_true')
    parser.add_argument('-d', '--debug',
                        help='Enable debug', action='store_true')
    parser.add_argument('-m', '--minimal_verbose',
                        help='Enable minimal verbosity', action='store_true')
    parser.add_argument('-s', '--synchronize',
                        help='Synchronize differences', action='store_true')
    parser.add_argument('--ignore-not-existing',
                        help='Ignore not-existing files', action='store_true')
    parser.add_argument('--ignore-file-differences',
                        help='Ignore file differences', action='store_true')
    parser.add_argument('--ignore-files-only-dirs',
                        help='Ignore files; only focuses on dirs',
                        action='store_true')
    parser.add_argument('--delete-orphan-files',
                        help='Delete orphan path2 files. '
                             'CAUTION is to be applied!', action='store_true')

    args = parser.parse_args()
    dryrun = not args.production or get_env_var('DRYRUN')
    debug = args.debug or get_env_var('DEBUG')
    verbose = args.verbose or get_env_var('VERBOSE') or debug
    minimal_verbose = args.minimal_verbose or get_env_var('MINIMAL_VERBOSE')
    if args.production and not args.synchronize:
        fatal_error('Pointless production run while not synchronizing. '
                    'Give -s -p instead.')
    project_filter = args.project_filter
    artist_filter = args.artist_filter
    album_filter = args.album_filter
    title_filter = args.title_filter

    if title_filter and title_filter.lower().endswith(SONG_FILE_EXT):
        title_filter = title_filter[:-len(SONG_FILE_EXT)]

    mark_dry_or_production_run(dryrun)

    root1 = args.path1
    root2 = args.path2

    if not root1 or not root2:
        parser.print_help()
        return

    name1 = args.name1 or '1'
    name2 = args.name2 or '2'

    if args.recursive:
        if root1.endswith('/'):
            root1 = root1[:-1]  # needed for checks below
        if root2.endswith('/'):
            root2 = root2[:-1]  # needed for checks below

        if args.synchronize:
            stdout('=== Diff\'ing and Syncing music files ===\n')
        else:
            stdout('=== Diff\'ing music files ===\n')

        stdout('SOURCE:', root1)
        stdout('TARGET:', root2)
        if project_filter:
            stdout('PROJECT FILTER:', project_filter)
        if artist_filter:
            stdout('ARTIST FILTER:', artist_filter)
        if album_filter:
            stdout('ALBUM FILTER:', album_filter)
        if title_filter:
            stdout('TITLE FILTER:', title_filter)

        stdout()

        cnt = diff_files(root1, root2, name1, name2,
                         args.ignore_files_only_dirs,
                         args.ignore_not_existing,
                         args.ignore_file_differences,
                         args.extended,
                         args.synchronize,
                         project_filter=project_filter,
                         artist_filter=artist_filter,
                         album_filter=album_filter,
                         title_filter=title_filter,
                         dryrun=dryrun,
                         verbose=verbose, minimal_verbose=minimal_verbose,
                         debug=debug)
        if minimal_verbose:
            stdout('\bCOMPLETE\n')
        elif cnt:
            stdout()
        diff_cnt = cnt

        if not args.ignore_not_existing and args.delete_orphan_files:
            stdout('CHECKING TARGET FOR ORPHANS (MIND!)')
            stdout()
            cnt = diff_files(root2, root1, name2, name1,  # mind, swapped
                             args.ignore_files_only_dirs,
                             synchronize=args.synchronize,
                             delete_root1_files_only=True,  # in reality root2
                             project_filter=project_filter,
                             artist_filter=artist_filter,
                             album_filter=album_filter,
                             title_filter=title_filter,
                             dryrun=dryrun,
                             verbose=verbose, minimal_verbose=minimal_verbose,
                             debug=debug)
            if minimal_verbose:
                stdout('\bCOMPLETE\n')
            elif cnt:
                stdout()
            diff_cnt += cnt

        if diff_cnt:
            if args.synchronize:
                stdout(diff_cnt, 'diffs corrected')
            else:
                stdout(diff_cnt, 'diffs observed')
        else:
            stdout('No diff observed')

    elif diff_tags(root1, root2, name1, name2):
        red('Different')
    else:
        green('Equal')


if __name__ == "__main__":
    main()
