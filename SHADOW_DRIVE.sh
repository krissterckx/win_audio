#!/bin/bash

. __lib/functions.sh

WIN_AUDIO_PATH=$PWD

if [[ ! $SOURCE ]];then
    SOURCE=~/Drive_Music
fi
if [[ ! $TARGET ]];then
    TARGET=~/Music
fi

EXIT_ON_FAILURE=1 MUSIC_DRIVE=$SOURCE check_drive

function shadow_dir {
    p=${PWD/$SOURCE/$TARGET}
    if [[ ! -d "$p/$1" ]];then
        $DO mkdir "$p/$1"
    fi
}

function shadow_file {
    cur=$PWD
    p=${PWD/$SOURCE/$TARGET}
    f=${1/.flac/.json}
    # ------------
    FROM="$cur/$1"
    TO="$p/$1"
    TO_S="$p/$f"
    # ------------
    if [[ $2 == '--overwrite' || ! -f "$TO_S" ]];then
        yellow "${DRYRUN_TAG}Shadowing $TO_S"
        cd "$WIN_AUDIO_PATH" || exit
        $DO python print_tags.py -x "$FROM" -e -f "$TO_S"
        cd "$cur" || exit

        if [[ -f "$TO" ]]; then
            if [[ ! $(diff "$FROM" "$TO") ]];then
                yellow "${DRYRUN_TAG}Deleting $TO"
                $DO rm -f "$TO"
            else
                red "$TO is different from $FROM! Skipped delete."
            fi
        fi
    fi
}

process_cmd_line_arguments --help-subscript "Scan your drive ($SOURCE) and shadow it locally ($TARGET). Local .flac files are DELETED when being (identical and) shadowed." "$@"
mark_dry_or_production_run

function fix_project {
    shadow_dir "$1"
}

function fix_artist {
    shadow_dir "$1"
}

function fix_album {
    shadow_dir "$1"
}

function fix_song {
    shadow_file "$1"  # --overwrite  # set flag to overwrite existing shadow f.
}

iterate_music_tree $SOURCE
