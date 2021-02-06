import argparse
import os

from __lib.base import stdout, get_env_var, assert_non_empty_dir, \
    assure_not_endswith
from __lib.functions import get_default_root, print_songs


def main():
    program = 'list_songs'
    description = '''
    Lists a set of songs'''

    parser = argparse.ArgumentParser(prog=program,
                                     description=description)
    parser.add_argument('-x', '--path', type=str,
                        help='Set root path')
    parser.add_argument('-a', '--artist-filter', type=str,
                        help='Set artist filter')
    parser.add_argument('-b', '--album-filter', type=str,
                        help='Set album filter')
    parser.add_argument('-c', '-t', '--title-filter', type=str,
                        help='Set title filter')
    parser.add_argument('-np', '--no-paths',
                        help='Don\'t print paths', action='store_true')
    parser.add_argument('-po', '--paths-only',
                        help='Print paths only', action='store_true')
    parser.add_argument('--dos',
                        help='Use DOS path format', action='store_true')
    parser.add_argument('--windows',
                        help='Use Windows path format', action='store_true')
    parser.add_argument('--detailed',
                        help='Enable detailed output', action='store_true')
    parser.add_argument('-e', '--extended',
                        help='get extended tags (only matters when detailed',
                        action='store_true')
    parser.add_argument('-v', '--verbose',
                        help='Enable verbose', action='store_true')
    parser.add_argument('-s', '--silent',
                        help='Enable silence', action='store_true')
    parser.add_argument('-d', '--debug',
                        help='Enable debug', action='store_true')

    args = parser.parse_args()
    root = args.path or get_default_root()
    detailed = args.detailed
    extended = args.extended
    silent = args.silent or get_env_var('SILENT')
    debug = args.debug or get_env_var('DEBUG')
    verbose = args.verbose or get_env_var('VERBOSE') or debug

    root = assure_not_endswith(root, '/')
    assert_non_empty_dir(root)
    listed = 0

    for dir_name, _, filenames in os.walk(root):
        c, _ = print_songs(dir_name, filenames,
                           artist_filter=args.artist_filter,
                           album_filter=args.album_filter,
                           title_filter=args.title_filter,
                           detailed=detailed,
                           extended=extended,
                           sort_per_track=True,
                           warn_for_inconsistencies=not silent,
                           print_paths=verbose and not args.no_paths,
                           path_only=args.paths_only,
                           dos_format=args.dos,
                           windows_format=args.windows,
                           verbose=verbose,
                           silent=silent,
                           debug=debug)

        if c and not verbose:
            stdout()
            listed += c

    stdout(listed, 'songs listed.')


if __name__ == "__main__":
    main()
