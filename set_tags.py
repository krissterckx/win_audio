import argparse

from lib.base import mark_dry_or_production_run, get_env_var
from lib.song import Song


def set_and_print(song_f, subscript, dryrun=True, debug=False, **kwargs):
    s = Song(song_f=song_f, debug=debug)
    s.set_tags(save=True, dryrun=dryrun, **kwargs)
    s.print_tags(subscript=subscript)


def main():
    program = 'set_tags'
    description = '''
    Sets tags of a music file. Set to 'None' to clear.'''

    parser = argparse.ArgumentParser(prog=program,
                                     description=description)

    tag_options = {
        'album': '-a',
        'albumartist': '-b',
        'artist': '-c',  # contributing artists
        'title': '-t',
        'tracknumber': '-n'
    }
    extended_tag_options = [
        'artwork', 'comment', 'compilation', 'composer',
        'discnumber', 'genre', 'lyrics', 'year', 'totaldiscs', 'totaltracks'
    ]
    parser.add_argument('-p', '--production', help='Enable production run',
                        action='store_true')
    parser.add_argument('-d', '--debug', help='Enable debug',
                        action='store_true')
    parser.add_argument('-x', '--path', type=str, help='path to music file')

    for tag, shortcut in tag_options.items():
        parser.add_argument(shortcut, '--' + tag, type=str, help=tag)
    for tag in extended_tag_options:
        parser.add_argument('--' + tag, type=str, help=tag)

    args = parser.parse_args()
    dryrun = not args.production or get_env_var('DRYRUN')
    debug = args.debug or get_env_var('DEBUG')

    parse_ok = False
    kwargs = {}
    if args.path:
        for t in list(tag_options) + extended_tag_options:
            if hasattr(args, t) and getattr(args, t):
                kwargs[t] = getattr(args, t)
                parse_ok = True
    if parse_ok:
        mark_dry_or_production_run(dryrun)
        set_and_print(args.path, 'Unmodified tags' if dryrun else None,
                      dryrun, debug, **kwargs)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
