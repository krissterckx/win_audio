#!/bin/bash


if [[ $1 == '-h' || $1 == '--help' ]];then
    echo "Use as:"
    echo "    $0 [-e|--extended] [-p|--production]"
    exit
fi
if [[ ! $LOCAL_SHADOW ]];then
    if [[ -d ~/Music_Shadow && -d ~/Music ]];then
        LOCAL_SHADOW=~/Music_Shadow
        LOCAL_FLAC=~/Music
    elif [[ -d ~/Music ]];then
        LOCAL_SHADOW=~/Music
    else
        echo "ERROR: cannot derive LOCAL_SHADOW"
        exit
    fi
fi
if [[ ! $DRIVE_FLAC ]];then
    if [[ -d ~/Drive_Music ]];then
        DRIVE_FLAC=~/Drive_Music
    else
        echo "ERROR: cannot derive DRIVE_FLAC"
        exit
    fi
fi

echo
echo "LOCAL_SHADOW = $LOCAL_SHADOW"
echo "LOCAL_FLAC   = $LOCAL_FLAC"
echo "DRIVE_FLAC   = $DRIVE_FLAC"

if [[ $NO_EXE ]];then
    exit
fi

if [[ -d $DRIVE_FLAC && -d $LOCAL_SHADOW ]];then
echo
echo "============"
echo "FORWARD SYNC: $LOCAL_SHADOW -> $DRIVE_FLAC"
echo "============"
echo

SOURCE=$LOCAL_SHADOW TARGET=$DRIVE_FLAC ./COPY_TO_DRIVE.sh "$@"  # will copy flac files to drive
fi

if [[ -d $DRIVE_FLAC && -d $LOCAL_FLAC ]];then
echo
echo "============"
echo "FORWARD SYNC: $LOCAL_FLAC -> $DRIVE_FLAC"
echo "============"
echo

SOURCE=$LOCAL_FLAC TARGET=$DRIVE_FLAC ./COPY_TO_DRIVE.sh "$@"  # will copy flac files to drive
fi

if [[ -d $DRIVE_FLAC && -d $LOCAL_SHADOW ]];then
echo
echo "========="
echo "SHADOWING: $DRIVE_FLAC -> $LOCAL_SHADOW"
echo "========="
echo

SOURCE=$DRIVE_FLAC TARGET=$LOCAL_SHADOW ./SHADOW_DRIVE.sh "$@"  # will shadow them and delete flac's locally
fi

if [[ -d $DRIVE_FLAC && -d $LOCAL_FLAC ]];then
echo
echo "============="
echo "BACKWARD SYNC: $DRIVE_FLAC -> $LOCAL_FLAC"
echo "============="
echo

SOURCE=$DRIVE_FLAC TARGET=$LOCAL_FLAC ./COPY_FROM_DRIVE.sh "$@"  # will copy flac files from drive
fi
