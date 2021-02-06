#!/bin/bash

# hint:
# set DIRS_ONLY for a quick dir scan only

. __lib/functions.sh

if [[ ! $SOURCE ]];then
    SOURCE=~/Drive_Music
fi
if [[ ! $TARGET ]];then
    TARGET=~/Music
fi

process_cmd_line_arguments --help-subscript "Scan your drive ($SOURCE) and perform a deep diff with your local store ($TARGET)." --no-arg-parsing "$@"
if [[ $NEED_MORE_HELP ]]; then
    echo
    python diff_songs.py -h | grep "^  -"
    exit
fi

EXIT_ON_FAILURE=1 MUSIC_DRIVE=$SOURCE check_drive

if [[ $DIRS_ONLY ]]; then
    OPTIONS='--ignore-files-only-dirs'  # for a quick dir scan only
fi

python diff_songs.py -x1 $SOURCE -x2 $TARGET -n1 'Drive' -n2 'Local' -r -e -m $OPTIONS "$@"  # add -s for sync and -p for production
