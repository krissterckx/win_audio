#!/bin/bash

# WARN : world hunger is not fixed
# pass -p for production run!

. __lib/functions.sh

function display_help {
    echo "Use as:"
    echo "    $0 [-x MUSIC_PATH] [--full] [-p]"
    echo
    echo "    Or use [-h|--help] for help."
    echo
    exit
}

if [[ $1 == '-h' || $1 == '--help' ]]; then
    display_help

elif [[ $1 == '-x' ]]; then
    shift
    export MUSIC=$1
    shift
fi
if [[ $1 == '--full' ]]; then
    FULL=1
    shift
fi
if [[ $1 && $1 != '-p' || $2 ]]; then
    display_help
fi

echo
if [[ $FULL ]]; then
TWEET=1 run ./fix_permissions.sh "$@"
echo
fi
TWEET=1 run python fix_non_flac.py "$@"
echo
TWEET=1 run python audit_songs.py
echo
TWEET=1 run python fix_track_nbrs.py -s "$@"
echo
TWEET=1 run python fix_empty_dirs.py "$@"
