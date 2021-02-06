import argparse
import os

from __lib.base import stdout, mark_dry_or_production_run, \
    make_dir, copy_file, assert_non_empty_dir, get_env_var
from __lib.functions import get_default_root, get_default_album_art_root, \
    ALBUM_ART_EXT


def main():
    program = 'copy_album_art'
    description = '''
    Copies album art'''

    parser = argparse.ArgumentParser(prog=program,
                                     description=description)
    parser.add_argument('-p', '--production',
                        help='production run', action='store_true')
    parser.add_argument('-x', '--path', type=str,
                        help='path to music file or dir of music files')
    parser.add_argument('-a', '--album_art_path', type=str,
                        help='destination path for music art')
    parser.add_argument('-r', '--recursive',
                        help='treat paths recursively', action='store_true')
    parser.add_argument('-v', '--verbose',
                        help='enables verbosity', action='store_true')
    parser.add_argument('-s', '--silent', help='enables silence',
                        action='store_true')

    args = parser.parse_args()
    dryrun = not args.production or get_env_var('DRYRUN')
    verbose = args.verbose or get_env_var('VERBOSE')
    silent = args.silent or get_env_var('SILENT')

    root = args.path or get_default_root()
    assert_non_empty_dir(root)
    mark_dry_or_production_run(dryrun)

    dest = args.album_art_path or get_default_album_art_root(
        dryrun=dryrun, verbose=verbose)
    assert_non_empty_dir(dest)

    if root and dest:
        if args.recursive:
            if root.endswith('/'):
                root = root[:-1]  # needed for checks below
            if dest.endswith('/'):
                dest = dest[:-1]  # needed for checks below

            stdout('SOURCE:', root)
            stdout('TARGET:', dest)
            stdout()

            for dir_name, _, file_names in os.walk(root):
                if dir_name == root:
                    continue
                else:
                    unrooted = dir_name.replace(root + '/', '')
                make_dir(dest, unrooted, conditionally=True, dryrun=dryrun,
                         verbose=verbose, silent=silent)
                for f in file_names:
                    for album_art_ext in ALBUM_ART_EXT:
                        if f.endswith(album_art_ext):
                            copy_file(root + '/' + unrooted + '/' + f,
                                      dest + '/' + unrooted + '/' + f,
                                      dryrun=dryrun,
                                      verbose=verbose, silent=silent)
        else:
            stdout('Non-recursive not implemented yet')

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
