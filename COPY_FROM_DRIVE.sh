#!/bin/bash

. __lib/functions.sh

if [[ ! $SOURCE ]];then
    SOURCE=~/Drive_Music
fi
if [[ ! $TARGET ]];then
    TARGET=~/Music
fi

process_cmd_line_arguments --help-subscript "Copy your drive ($SOURCE) to your local store ($TARGET)." --no-arg-parsing "$@"
if [[ $NEED_MORE_HELP ]]; then
    echo
    python diff_songs.py -h | grep "^  -"
    exit
fi

EXIT_ON_FAILURE=1 MUSIC_DRIVE=$SOURCE check_drive

if ! find_cmd_line_argument '-e' "$@" && ! find_cmd_line_argument '--extended' "$@"; then
    green "WARN: By default this is a quick file check/copy only. Give '-e' for extended tags check."
fi
if ! find_cmd_line_argument '--delete-orphan-files' "$@"; then
    green "INFO: Give --delete-orphan-files for deleting orphans. CAUTION: do not apply when you have extra files."
fi

python diff_songs.py -x1 $SOURCE -x2 $TARGET -n1 'Drive' -n2 'Local' -r -s "$@"  # add -e for extended; add -p for production
