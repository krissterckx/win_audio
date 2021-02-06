#!/bin/bash

# DEPRECATED ; WILL BE REMOVED

. __lib/functions.sh

function fix_me {
    orig=$1
    fixed=$orig
    SKIP='ring-a- a-ha un- zoot- holi- da- re- doo- chow- ne- hip- man- bel- day- drive- hit- x- nik- vas- h-town tech- all- wu- \-knox can- chi \-oh \-a-way \-bas super- on- \-n- \-o.k. \-side \-moi \-toi \-vous \-je peut- \-gram \-it \-one hi- \-up auto- in- go- 1-900- saint- \-lo ab-i \-man ab- jay- death- bur- \-mix \-hiker khz- scott-'  # lower-case!

    # shellcheck disable=SC2086
    if grep -q - <<< $orig; then
        for c in {A..Z}; do
            # shellcheck disable=SC2086
            if grep -q $c- <<< $orig; then
                return
            fi
        done
        for k in $SKIP; do
            # shellcheck disable=SC2086
            if grep -q -i $k <<< $orig; then
                return
            fi
        done
        for c in {a..z} {A..Z}; do  # don't add numbers, like phone numbers e.g must stay
            fixed=${fixed//$c-/$c -}
            fixed=${fixed//-$c/- $c}
        done
        if [[ $fixed != "$orig" ]]; then  # keep quotes
            TWEET=1 $DO mv "$orig" "$fixed"  # keep quotes - this only works then
        fi
    fi
    if [[ ! $PRODUCTION_RUN ]]; then
        fixed=$orig  # restore
    fi
}

if [[ $1 == '-s' || $1 == '--silent' ]]; then
    # shellcheck disable=SC2034
    SILENT=1

elif [[ $1 == '-p' || $1 == '--production' ]]; then
    # shellcheck disable=SC2034
    PRODUCTION_RUN=1

    if [[ $2 == '-v' || $2 == '--verified' ]]; then
         # shellcheck disable=SC2034
         PRODUCTION_RUN_VERIFIED=1
    fi

elif [[ $1 ]]; then
    echo "Use as:"
    echo "    $0"
    echo
    echo "Example run:"
    echo "    $0 -p"
    echo "or:"
    echo "    PRODUCTION_RUN=1 $0"
    echo "or:"
    echo "    $0 -s  # silent"
    echo "or:"
    echo "    $0 -p -v  # verified production run"
    echo "or, e.g.:"
    echo "    MUSIC=/cygdrive/E/MUSIC SILENT=1 FILTER_PROJECT=Tidal FILTER_ARTIST='The Opposites' $0"
    echo
    exit
fi

mark_dry_or_production_run --production-run-must-be-verified

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
