#!/bin/bash

. __lib/functions.sh

if [[ ! $SOURCE ]];then
    SOURCE=~/Music
fi
if [[ ! $TARGET ]];then
    TARGET=~/Drive_Music
fi

process_cmd_line_arguments --help-subscript "Copy your local store ($SOURCE) to your drive ($TARGET)." --no-arg-parsing "$@"
if [[ $NEED_MORE_HELP ]]; then
    echo
    python diff_songs.py -h | grep "^  -"
    exit
fi

EXIT_ON_FAILURE=1 MUSIC_DRIVE=$TARGET check_drive

if ! find_cmd_line_argument '-e' "$@" && ! find_cmd_line_argument '--extended' "$@"; then
    green "WARN: By default this is a quick file check/copy only. Give '-e' for extended tags check."
fi
if ! find_cmd_line_argument '--delete-orphan-files' "$@"; then
    green "INFO: Give --delete-orphan-files for deleting orphans. CAUTION: do not apply when you have extra files."
fi

python diff_songs.py -x1 $SOURCE -x2 $TARGET -n1 'Local' -n2 'Drive' -r -s "$@"  # add -e for extended; add -p for production
