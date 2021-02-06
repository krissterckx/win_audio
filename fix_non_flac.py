import argparse
import os

from __lib.base import stdout, assert_non_empty_dir, remove_file, \
    mark_dry_or_production_run, get_env_var, yellow
from __lib.functions import SONG_FILE_EXT, ALBUM_ART_EXT, MISSING_MARK_EXT, \
    REVIEWED_MARK_EXT, get_default_root, is_song_file

REVIEWED_EXTENSIONS = [
    REVIEWED_MARK_EXT
]
MISSING_EXTENSIONS = [
    MISSING_MARK_EXT
]
TOLERATED_FILE_EXTENSIONS = REVIEWED_EXTENSIONS + MISSING_EXTENSIONS


def main():
    program = 'fix_non_flac'
    description = '''
    Fix non-FLAC songs'''

    parser = argparse.ArgumentParser(prog=program, description=description)
    parser.add_argument('-x', '--path', type=str, help='Root path')
    parser.add_argument('-p', '--production', help='Enable production run',
                        action='store_true')
    parser.add_argument('-ir', '--include-reviewed-files',
                        help='Include .reviewed files',
                        action='store_true')
    parser.add_argument('-f', '--full',
                        help='Full clean, including tolerated extensions',
                        action='store_true')
    parser.add_argument('-fa', '--full-including-album-art',
                        help='Full clean, including album art and '
                             'tolerated extensions',
                        action='store_true')
    parser.add_argument('-v', '--verbose', help='Enable verbosity',
                        action='store_true')
    parser.add_argument('-s', '--silent', help='Enable silence',
                        action='store_true')
    parser.add_argument('-d', '--debug', help='Enable debug',
                        action='store_true')
    args = parser.parse_args()
    root = args.path or get_default_root()
    dryrun = not args.production or get_env_var('DRYRUN')
    silent = args.silent or get_env_var('SILENT')
    debug = args.debug or get_env_var('DEBUG')
    verbose = args.verbose or get_env_var('VERBOSE') or debug

    assert_non_empty_dir(root)
    mark_dry_or_production_run(dryrun)
    cnt = 0

    if args.full_including_album_art:
        protected_extensions = []
    elif args.full:
        protected_extensions = ALBUM_ART_EXT
    elif args.include_reviewed_files:
        protected_extensions = MISSING_EXTENSIONS + ALBUM_ART_EXT
    else:
        protected_extensions = TOLERATED_FILE_EXTENSIONS + ALBUM_ART_EXT

    def protected():
        for extension in protected_extensions:
            if file_name.lower().endswith(extension):
                return True
        return False

    for dir_name, _, file_names in os.walk(root):
        for file_name in file_names:
            if not is_song_file(file_name):
                if not protected():
                    yellow('Deleting', dir_name + '/' + file_name)
                    remove_file(dir_name, file_name, False,
                                dryrun=dryrun, verbose=verbose, silent=silent,
                                debug=debug)
                    cnt += 1
    if cnt:
        stdout()
    stdout(cnt, 'non-{} files deleted.'.format(SONG_FILE_EXT[1:]))


if __name__ == "__main__":
    main()
