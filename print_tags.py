import argparse
import os

from __lib.base import stdout, is_dir, fatal_error
from __lib.functions import SONG_FILE_EXT, get_default_root
from __lib.song import Song


def print_tags(song_f=None, detailed=False,
               as_json=False, as_pprint=False, to_file=None,
               extended=False, header=True,
               subscript=None, highlight_title=False, debug=False):
    if debug:
        stdout('print_tags', song_f, detailed, as_json, as_pprint, to_file,
               extended, header, subscript, highlight_title)
    Song(song_f=song_f, debug=debug).print_tags(
        detailed, as_json, as_pprint, to_file, extended, header, subscript,
        highlight_title)


def main():
    program = 'print_tags'
    description = '''
    Prints tags of a music file or recursively within a music files directory
    '''

    parser = argparse.ArgumentParser(prog=program,
                                     description=description)
    parser.add_argument('-x', '--path', type=str,
                        help='path to music file or to music files directory')
    parser.add_argument('-r', '--recursive',
                        help='walk-thru path recursively', action='store_true')
    parser.add_argument('-e', '--extended',
                        help='get extended tags', action='store_true')
    parser.add_argument('-f', '--to-file', type=str,
                        help='print to file')
    parser.add_argument('-d', '--debug',
                        help='Enable debug', action='store_true')
    args = parser.parse_args()

    if args.recursive:
        stdout()
        root = args.path if args.path else get_default_root()
        for dir_name, _, file_names in os.walk(root):
            for file_name in file_names:
                if file_name.lower().endswith(SONG_FILE_EXT):
                    print_tags(dir_name + '/' + file_name,
                               extended=args.extended, debug=args.debug)

    elif args.path:
        path = args.path
        if is_dir(path):
            fatal_error('Specified path is directory; pass -r option or '
                        'be more specific')
        elif path.lower().endswith(SONG_FILE_EXT):
            print_tags(path, as_json=True, to_file=args.to_file or None,
                       extended=args.extended, debug=args.debug)
        else:
            fatal_error('Specified path is not a song')

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
