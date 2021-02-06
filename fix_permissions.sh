#!/bin/bash

. __lib/functions.sh

function fix_me {
    # shellcheck disable=SC2086
    SILENT=1 $DO chown $USER "$1"  # keep quotes
    # shellcheck disable=SC2086
    SILENT=1 $DO chmod 755 "$1"  # keep quotes
}

process_cmd_line_arguments --help-subscript "Fix permissions of your music store. Must be run as administrator." "$@"
mark_dry_or_production_run --production-run-must-be-run-as-admin

function fix_project {
    fix_me "$1"
}

function fix_artist {
    fix_me "$1"
}

function fix_album {
    fix_me "$1"
}

function fix_song {
    fix_me "$1"
}

iterate_music_tree
