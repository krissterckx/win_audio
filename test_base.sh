#!/bin/bash

WIN_AUDIO_STYLE_BASE=1 . __lib/base.sh

if is_cygwin; then
    yellow "You are on Cygwin"
else
    cyan "You are not on Cygwin"
fi
echo

if [[ $1 == '-s' ]]; then
   # shellcheck disable=SC2034
   SILENT=1
fi

output_no_newline 'Tomatoes are '
in_red_no_newline "red"
output_no_newline ' and grapes are '
in_blue 'blue.'

out_no_newline 'Even when silenced, tomatoes are '
red_no_newline "red"
out_no_newline ' and grapes are '
blue 'blue.\n'

# shellcheck disable=SC2086
blue_cat $0

if ! check_dir_non_empty lib; then
    fatal_error "check_dir_non_empty lib failure (got $?)"
fi
mkdir grease_is_the_word
if check_dir_non_empty grease_is_the_word; then
    fatal_error 'check_dir_non_empty grease_is_the_word failure'
fi
rmdir grease_is_the_word
