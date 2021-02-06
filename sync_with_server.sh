#!/bin/bash

WIN_AUDIO_STYLE_BASE=1 . __lib/base.sh
DIR=$1
TARGET=${DIR//Drive_Music/Music}  # a bit of a dirty hack. When you sync from drive...

if [[ ! $1 || $1 == '-h' || $1 == '--help' ]];then
    echo "Use as:"
    echo "    [LOCAL=1] [SONG=abc.flac] [VERBOSE=1] $0 <dir> (that must be a dir holding flac's) [-p]"
    exit

elif [[ ! -d $DIR ]];then
    error --fatal "$DIR does not exist!"

elif [[ $2 == '-p' ]];then
    # shellcheck disable=SC2034
    PRODUCTION_RUN=1
fi

if [[ ! $REMOTE ]];then
    if [[ $DEFAULT_REMOTE ]];then
        REMOTE=$DEFAULT_REMOTE
    else
        error --fatal "Need to pass REMOTE"
    fi
fi
if [[ ! $WHOM ]];then
    WHOM=$ME
fi
if [[ ! $PASS ]];then
    if [[ $SECRET_PASS ]];then
        PASS=$SECRET_PASS
    else
        error --fatal "Need to pass PASS"
    fi
fi
cd "$DIR" || exit
if [[ ! $(ls -- *.flac) ]];then
    error --fatal "There are no flac's in $DIR; exiting"
fi

mark_dry_or_production_run

# ------------------------------ main logic -----------------------------------

# shellcheck disable=SC2034
error_silent=$SILENT

if [[ $SONG ]]; then

    remote_mkdir "$WHOM" "$PASS" "$REMOTE" "$TARGET"
    scp_file "$WHOM" "$PASS" "$REMOTE" "$DIR$SONG" "$TARGET$SONG"

else

    scp_dir "$WHOM" "$PASS" "$REMOTE" "$DIR" "$TARGET"

fi
