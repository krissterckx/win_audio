# DEPRECATED ; WILL BE REMOVED

import argparse
import os

from __lib.base import stdout, cyan, warn, alert, mark_dry_or_production_run, \
    remove_file, rename_file, get_env_var, assert_non_empty_dir, \
    assure_not_endswith
from __lib.functions import SONG_FILE_EXT, get_default_root
from __lib.song import Song


def fix_indexed_songs(path, song_fs, dryrun=True, safe_remove=True,
                      verbose=False, silent=False, debug=False):

    def report(*args, **kwargs):
        force = False
        if 'force' in kwargs:
            force = kwargs['force']
            kwargs.pop('force')
        if force or not silent:
            cyan(*args, **kwargs)

    def retag(song, new_title):
        if not silent:
            stdout('Retagging to', new_title)
        song.set('TITLE', new_title)
        song.save(dryrun)

    cnt = 0

    for song_f in song_fs:
        for i in range(99):
            suffix = ' (' + str(i) + ')' + SONG_FILE_EXT
            if song_f.endswith(suffix):
                stripped = song_f[:-len(suffix)]
                stripped_f = stripped + SONG_FILE_EXT
                s = Song(path=path, song_f=song_f, debug=debug)

                if stripped_f in song_fs:
                    report('Resolving conflict with', stripped_f)
                    t = s.parse_track_nbr()
                    s_stripped = Song(path=path, song_f=stripped_f,
                                      debug=debug)
                    t_stripped = s_stripped.parse_track_nbr()
                    stripped_j = song_f[:-len(SONG_FILE_EXT)]  # reasonable
                    stripped_j_f = song_f  # -                   defaults
                    for j in range(2, 99):
                        stripped_j = stripped + ' -' + str(j) + '-'
                        stripped_j_f = stripped_j + SONG_FILE_EXT
                        if stripped_j_f not in song_fs:
                            break
                    if t < t_stripped:
                        report('New', song_f, 'becomes', stripped_f,
                               # and original stripped becomes stripped_j
                               'as its track number is lower', force=True)
                        retag(s, stripped)
                        rename_file(path, song_f, stripped_f,
                                    dryrun=dryrun,
                                    verbose=verbose, silent=silent,
                                    debug=debug)
                        retag(s_stripped, stripped_j)
                        rename_file(path, stripped_f, stripped_j_f,
                                    dryrun=dryrun, safe_rename=not dryrun,
                                    verbose=verbose, silent=silent,
                                    debug=debug)
                    elif t > t_stripped:
                        report('New', song_f, 'becomes', stripped_j_f,
                               # and original stripped remains
                               'as its track number is higher', force=True)
                        retag(s, stripped_j)
                        rename_file(path, song_f, stripped_j_f,
                                    dryrun=dryrun,
                                    verbose=verbose, silent=silent,
                                    debug=debug)
                    else:
                        report('Track numbers match!')
                        report('Comparing sample rates')
                        s1 = int(s.get('#samplerate'))
                        s2 = int(s_stripped.get('#samplerate'))
                        if s1 > s2:
                            report('New', song_f, 'wins (' + str(s1),
                                   'over', str(s2) + ')', force=True)
                            alert('Removing', path, stripped_f)
                            remove_file(path, stripped_f,
                                        safe_remove=safe_remove, dryrun=dryrun,
                                        verbose=verbose, silent=silent,
                                        debug=debug)
                            retag(s, stripped)
                            rename_file(path, song_f, stripped,
                                        dryrun=dryrun, safe_rename=not dryrun,
                                        verbose=verbose, silent=silent,
                                        debug=debug)
                        elif s1 < s2:
                            report('Existing', stripped_f, 'wins (' + str(s2),
                                   'over', str(s1) + ')', force=True)
                            alert('Removing', path, song_f)
                            remove_file(path, song_f,
                                        safe_remove=safe_remove, dryrun=dryrun,
                                        verbose=verbose, silent=silent,
                                        debug=debug)
                        else:
                            report('Sample rates match!')
                            report('Comparing length')
                            l1 = int(s.get('#length'))
                            l2 = int(s_stripped.get('#length'))
                            if l1 > l2:
                                cyan('New', song_f, 'wins (' + str(l1),
                                     'over', str(l2) + ')', force=True)
                                alert('Removing', path, song_f)
                                remove_file(path, stripped_f,
                                            safe_remove=safe_remove,
                                            dryrun=dryrun,
                                            verbose=verbose, silent=silent,
                                            debug=debug)
                                retag(s, stripped)
                                rename_file(path, song_f, stripped_f,
                                            dryrun=dryrun,
                                            safe_rename=not dryrun,
                                            verbose=verbose, silent=silent,
                                            debug=debug)
                            else:
                                report('Existing', stripped_f,
                                       'wins (' + str(l2),
                                       'over', str(l1) + ')', force=True)
                                alert('Removing', path, song_f)
                                remove_file(path, song_f,
                                            safe_remove=safe_remove,
                                            dryrun=dryrun,
                                            verbose=verbose, silent=silent,
                                            debug=debug)
                else:
                    report('Fixing', song_f, 'to', stripped + SONG_FILE_EXT)
                    retag(s, stripped)
                    rename_file(path, song_f, stripped_f,
                                dryrun=dryrun,
                                verbose=verbose, silent=silent, debug=debug)

                cnt += 1

            if not dryrun and cnt:
                break

        if not dryrun and cnt:
            break

    return cnt


def fill_up_holes(root, file_names, dryrun=True, verbose=False, silent=False,
                  debug=False):
    for f in file_names:
        for i in range(3, 99):
            suffix = ' -' + str(i) + '-' + SONG_FILE_EXT
            if f.endswith(suffix):
                b = f[:-len(suffix)]
                prev = '{} -{}-{}'.format(b, i - 1, SONG_FILE_EXT)
                if prev not in file_names:
                    rename_file(root, f, prev,
                                dryrun=dryrun,
                                verbose=verbose, silent=silent, debug=debug)


def main():
    program = 'fix_indexed_songs'
    description = '''
    Fixes indexed songs'''

    parser = argparse.ArgumentParser(prog=program,
                                     description=description)
    parser.add_argument('-x', '--path', type=str, help='Root path')
    parser.add_argument('-v', '--verbose', help='Enable verbosity',
                        action='store_true')
    parser.add_argument('-s', '--silent', help='Enable silence',
                        action='store_true')
    parser.add_argument('-d', '--debug', help='Enable debug',
                        action='store_true')
    parser.add_argument('-p', '--production', help='Enable production run',
                        action='store_true')
    parser.add_argument('--safe-delete',  # create .deleted files always
                        # Mind - for remixes can be good idea to set
                        help='Safely delete files',
                        action='store_true')

    args = parser.parse_args()
    root = args.path or get_default_root()
    dryrun = not args.production or get_env_var('DRYRUN')
    silent = args.silent or get_env_var('SILENT')
    debug = args.debug or get_env_var('DEBUG')
    verbose = args.verbose or get_env_var('VERBOSE') or debug
    safe_delete = args.safe_delete

    root = assure_not_endswith(root, '/')
    assert_non_empty_dir(root)
    mark_dry_or_production_run(dryrun)
    cnt = 0

    if dryrun:
        warn('DRYRUN results are not representative!')
    if not safe_delete:
        warn('Redundant files WILL be deleted (to modify, give --safe-delete)')
        stdout('      '
               '(While only redundant files are deleted, '
               'in case of remix songs, it can be dangerous. ')
        stdout('      '
               ' In general, make sure diff songs have diff '
               'track numbers within a given dir.)')
        stdout()

    def verbose_report(*report_args, **report_kwargs):
        if verbose:
            cyan(*report_args, **report_kwargs)

    verbose_report('Reindexing files')
    while True:
        curr_cnt = cnt

        #
        # WARN : NOT MOST EFFICIENT IMPLEMENTATION! ... but it works :)
        #

        for dir_name, _, file_names in os.walk(root):
            if dir_name == root:
                continue
            else:
                unrooted = dir_name.replace(root + '/', '')

            cnt += fix_indexed_songs(root + '/' + unrooted, file_names,
                                     dryrun, safe_delete, verbose, silent,
                                     debug)

        changed_made = cnt - curr_cnt

        # keep looping if changes made in production run
        if dryrun or not changed_made:
            break

    # now check that we didn't create gaps, if so, fill them up
    verbose_report('Filling up holes')
    for dir_name, _, file_names in os.walk(root):
        unrooted = dir_name.replace(root + '/', '')
        fill_up_holes(root + '/' + unrooted, file_names, dryrun,
                      verbose, silent)

    if cnt:
        stdout()
    stdout(cnt, 'files were renamed.')


if __name__ == "__main__":
    main()
