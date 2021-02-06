import argparse
import os

from __lib.base import stdout, assert_non_empty_dir, get_env_var, \
    mark_dry_or_production_run, assure_not_endswith
from __lib.functions import get_default_root, get_filtered_songs, \
    process_songs_dir


def fix_track_nbrs(root, project, artist, album, songs,
                   artist_filter=None, album_filter=None,
                   title_filter=None, force_overwrite_total_tracks=None,
                   mark_missing_songs=False, dryrun=True,
                   verbose=False, silent=False, radio_silent=False,
                   debug=False):
    fixed_tracks = 0
    missed_tracks = 0
    warnings = 0
    dry = '(dryrun) ' if dryrun else ''

    songs_by_track_nbr, missed_songs, total_tracks, w, _ = get_filtered_songs(
        root + '/' + project + '/' + artist + '/' + album, songs,
        artist_filter, album_filter, title_filter,
        sort_per_track=True,
        post_process_songs=force_overwrite_total_tracks is None,
        print_header=verbose,
        no_warn=radio_silent, deep_warn=True,
        mark_missing_songs=mark_missing_songs, dryrun=dryrun,
        verbose=verbose, silent=silent, debug=debug)

    missed_tracks += len(missed_songs)
    warnings += w

    if total_tracks or force_overwrite_total_tracks:
        for track_nbr in sorted(songs_by_track_nbr):
            for song in songs_by_track_nbr[track_nbr]:
                title = song.get('TITLE')
                track_tag = song.get_track_nbr_as_string(
                    default=None, verbose=verbose)
                empty_tag = track_tag is None
                new_tag = '{}/{}'.format(track_nbr,
                                         force_overwrite_total_tracks
                                         if force_overwrite_total_tracks
                                         else total_tracks)
                if track_tag != new_tag:
                    stdout(dry + 'Fixing',
                           project, '/', artist, '/', album, '/', title, '/',
                           'empty track' if empty_tag else (
                                   'track ' + track_tag), 'to', new_tag)
                    song.set('TRACKNUMBER', new_tag, save=True, dryrun=dryrun)
                    fixed_tracks += 1

    return fixed_tracks, missed_tracks, warnings


def main():
    program = 'fix_track_nbrs'
    description = '''
    Fixes song track numbers'''

    parser = argparse.ArgumentParser(prog=program,
                                     description=description)
    parser.add_argument('-x', '--path', type=str,
                        help='Set root path')
    parser.add_argument('-j', '--project-filter', type=str,
                        help='Set project filter')
    parser.add_argument('-a', '--artist-filter', type=str,
                        help='Set artist filter')
    parser.add_argument('-b', '--album-filter', type=str,
                        help='Set album filter')
    parser.add_argument('-c', '-t', '--title-filter', type=str,
                        help='Set title filter')
    parser.add_argument('-m', '--missing-songs-stamps',
                        help='Create missing songs stamps',
                        action='store_true')
    parser.add_argument('--force-overwrite-total-tracks', type=int,
                        help='Force-overwrite tracks total')
    parser.add_argument('-p', '--production', help='Enable production run',
                        action='store_true')
    parser.add_argument('-v', '--verbose', help='Enable verbose',
                        action='store_true')
    parser.add_argument('-s', '--silent', help='Enable silence',
                        action='store_true')
    parser.add_argument('-rs', '--radio-silent', help='Enable radio silence',
                        action='store_true')
    parser.add_argument('-d', '--debug', help='Enable debug',
                        action='store_true')

    args = parser.parse_args()
    root = args.path or get_default_root()
    project_filter = args.project_filter
    artist_filter = args.artist_filter
    album_filter = args.album_filter
    title_filter = args.title_filter
    mark_missing_songs = args.missing_songs_stamps
    force_overwrite_total_tracks = args.force_overwrite_total_tracks
    dryrun = not args.production or get_env_var('DRYRUN')
    radio_silent = args.radio_silent or get_env_var('RADIO_SILENT')
    silent = args.silent or get_env_var('SILENT') or radio_silent
    debug = args.debug or get_env_var('DEBUG')
    verbose = args.verbose or get_env_var('VERBOSE') or debug

    root = assure_not_endswith(root, '/')  # makes dir_name / filename to be
    #                                        always correct
    assert_non_empty_dir(root)
    mark_dry_or_production_run(dryrun)

    if force_overwrite_total_tracks:
        assert artist_filter or album_filter or title_filter

    fixed = missed = warnings = 0
    for dir_name, _, filenames in os.walk(root):
        process, project, artist, album = process_songs_dir(
            root, dir_name, project_filter, artist_filter, album_filter)
        if not process:
            continue

        f, m, w = fix_track_nbrs(root, project, artist, album, filenames,
                                 title_filter=title_filter,
                                 mark_missing_songs=mark_missing_songs,
                                 force_overwrite_total_tracks=
                                 force_overwrite_total_tracks,
                                 dryrun=dryrun, verbose=verbose,
                                 silent=silent, radio_silent=radio_silent,
                                 debug=debug)
        fixed += f
        missed += m
        warnings += w

    if fixed or (missed and not silent) or (warnings and not radio_silent):
        stdout()
    stdout(fixed, 'tracks were fixed.')
    if missed and not silent:
        stdout(missed, 'tracks are missed.')
    if warnings and not radio_silent:
        stdout(warnings, 'warnings were raised.')


if __name__ == "__main__":
    main()
