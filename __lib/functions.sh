#!/bin/bash

if [[ ! $FUNCTIONS_SH_SOURCED ]];then

WIN_AUDIO_STYLE_BASE=1 . __lib/base.sh "$@"

if [[ ! $MUSIC ]]; then
    export MUSIC=~/Music
fi
if [[ ! $MUSIC_PROJECTS ]]; then
    export MUSIC_PROJECTS='SoundCloud SoundCloudGo Tidal'
fi

DEFAULT_MUSIC_DRIVE=~/Drive_Music  # don't quote
SONG_FILE_EXT='.flac'  # keep lower-case

function check_drive {
    if [[ ! $MUSIC_DRIVE ]];then
        MUSIC_DRIVE=$DEFAULT_MUSIC_DRIVE  # don't quote
    fi
    # shellcheck disable=SC2010
    debug "MUSIC_DRIVE = $MUSIC_DRIVE"
    if [[ -L $MUSIC_DRIVE ]];then
        DRIVE=$(ls -l $MUSIC_DRIVE 2>/dev/null| grep -E -o "\-> .*" | grep -E -o "/.*")
    else
        DRIVE=$MUSIC_DRIVE
    fi
    debug "DRIVE = $DRIVE"
    if ls -l "$DRIVE" >/dev/null 2>&1; then
        debug "Connected!"
        return
    else
        debug "Unconnected!"
        red 'Connect the drive!'
        if [[ $EXIT_ON_FAILURE ]]; then
            exit 1
        else
            false
        fi
    fi
}

function find_cmd_line_argument {
    debug "find_cmd_line_arguments $*"
    SEARCH=$1
    shift
    while [[ $1 ]]; do
        if [[ $1 == "$SEARCH" ]]; then
            return
        else
            shift
        fi
    done
    false
}

function process_cmd_line_arguments {
    debug "process_cmd_line_arguments $*"
    HELP_SUBSCRIPT=
    NEED_MORE_HELP=
    ARG_PARSING=1
    while true; do
        if [[ $1 == '--help-subscript' ]]; then
            HELP_SUBSCRIPT=$2
            shift
            shift
            continue
        elif [[ $1 == '--no-arg-parsing' ]]; then
            ARG_PARSING=
            shift
            continue
        elif [[ $ARG_PARSING && ($1 == '-v' || $1 == '--verbose') ]]; then
            # shellcheck disable=SC2034
            VERBOSE=1
            shift
            continue
        elif [[ $ARG_PARSING && ($1 == '-s' || $1 == '--silent') ]]; then
            # shellcheck disable=SC2034
            SILENT=1
            shift
            continue
        elif [[ $ARG_PARSING && ($1 == '-e' || $1 == '--extended') ]]; then
            # shellcheck disable=SC2034
            EXTENDED=1   # NOT USED SO DON'T ADVERTISE - DO NOT DELETE THOUGH
            shift
            continue
        elif [[ $ARG_PARSING && ($1 == '-p' || $1 == '--production') ]]; then
            # shellcheck disable=SC2034
            PRODUCTION_RUN=1
            shift
            continue
        elif [[ ($ARG_PARSING && $1) || $1 == '-h' || $1 == '--help' ]]; then
            if [[ $HELP_SUBSCRIPT ]];then
                echo "$HELP_SUBSCRIPT"
            fi
            echo "Use as:"
            if [[ $ARG_PARSING ]];then
                echo "    $0 [-v|-s|-p]"
                echo
                echo "Example run:"
                echo "    $0 -p"
            else
                echo "    $0 <see below args>"
                # shellcheck disable=SC2034
                NEED_MORE_HELP=1
                return
            fi
            echo
            exit
        else
            break
        fi
    done
}

# FILTER_PROJECT=Tidal
# FILTER_ARTIST='Fleetwood Mac'
# FILTER_ALBUM='Rumours (Deluxe Edition)'
# FILTER_SONG='World Turning (Live at The Fabulous Forum, Inglewood, CA 08-29-77) [2013 Remaster].flac'

function iterate_music_tree {
    if [[ $1 ]]; then
        MUSIC_ROOT=$1
    else
        MUSIC_ROOT=$MUSIC
    fi
    assert_non_empty_dir "$MUSIC_ROOT"
    cd "$MUSIC_ROOT" || exit  # keep quotes
    for project in $MUSIC_PROJECTS; do
        if ! check_dir_non_empty "$MUSIC_ROOT/$project"; then
            continue
        fi
        if [[ $FILTER_PROJECT && $project != "$FILTER_PROJECT" ]]; then
            continue
        fi
        yellow_verbose "Processing $project"
        fixed=
        fix_project "$project"  # keep quotes
        if [[ $fixed ]]; then
            if [[ $SILENT && $fixed != "$project" ]]; then
                yellow "($project/$artist$album$song)"
            fi
            project=$fixed
        fi
        cd "$project" || exit  # keep quotes
        for artist in */; do
            if [[ $FILTER_ARTIST && $artist != "$FILTER_ARTIST/" ]]; then
                continue
            fi
            yellow_verbose "Processing $project/$artist"
            fixed=
            fix_artist "$artist"  # keep quotes
            if [[ $fixed ]]; then
                if [[ $SILENT && $fixed != "$artist" ]]; then
                    yellow "($project/$artist)"
                fi
                artist=$fixed
            fi
            cd "$artist" || exit  # keep quotes
            for album in */; do
                if [[ $FILTER_ALBUM && $album != "$FILTER_ALBUM/" ]]; then
                    continue
                fi
                yellow_verbose "Processing $project/$artist$album"
                fixed=
                fix_album "$album"  # keep quotes
                if [[ $fixed ]]; then
                    if [[ $SILENT && $fixed != "$album" ]]; then
                        yellow "($project/$artist$album)"
                    fi
                    album=$fixed
                fi
                cd "$album" || exit  # keep quotes
                yellow_verbose "Processing $project/$artist$album..."
                for song in *"$SONG_FILE_EXT"; do
                    if [[ $FILTER_SONG && $song != "$FILTER_SONG" ]]; then
                        continue
                    fi
                    fixed=
                    fix_song "$song"  # keep quotes
                    if [[ $fixed ]]; then
                        if [[ $SILENT && $fixed != "$song" ]]; then
                            yellow "($project/$artist$album$song)"
                        fi
                    fi
                done
                cd ..
            done
            cd ..
        done
        cd ..
    done
}

FUNCTIONS_SH_SOURCED=1

fi

