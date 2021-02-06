#!/bin/bash

# hint:
# set DIRS_ONLY for a quick dir scan only

. __lib/functions.sh

if [[ ! $SOURCE ]];then
    SOURCE=~/Music
fi
if [[ ! $TARGET ]];then
    TARGET=~/Drive_Music
fi

process_cmd_line_arguments --help-subscript "Scan your local store ($SOURCE) and perform a deep diff with your drive ($TARGET)." --no-arg-parsing "$@"
if [[ $NEED_MORE_HELP ]]; then
    echo
    python diff_songs.py -h | grep "^  -"
    exit
fi

EXIT_ON_FAILURE=1 MUSIC_DRIVE=$TARGET check_drive

if [[ $DIRS_ONLY ]]; then
    OPTIONS='--ignore-files-only-dirs'  # for a quick dir scan only
fi

python diff_songs.py -x1 $SOURCE -x2 $TARGET -n1 'Local' -n2 'Drive' -r -e -m $OPTIONS "$@"  # add -s for sync and -p for production

