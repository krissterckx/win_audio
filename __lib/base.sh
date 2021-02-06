#!/bin/bash

# Kris Sterckx
# 2020 Nuage Networks

# -----------------------------------------------------------------------------

if [[ ! $BASE_SH_SOURCED ]];then

# shellcheck disable=SC2034
ID='id'
IP='[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+'
# shellcheck disable=SC2034
ALPHA='[A-Za-z0-9_\.\-]+'
# shellcheck disable=SC2034
NAME_REGEX='[A-Za-z0-9_\-]+'
# shellcheck disable=SC2034
EXTD_NAME='[A-Za-z0-9@_\.\(\)\-]+'
# shellcheck disable=SC2034
SPACED_NAME='[A-Za-z0-9_][ A-Za-z0-9_\-]*'
# shellcheck disable=SC2034
SPACED_EXTD_NAME='[A-Za-z0-9_][ A-Za-z0-9@_\.\(\)\-]*'

UUID='[0-9a-f]+-[0-9a-f]+-[0-9a-f]+-[0-9a-f]+-[0-9a-f]+'
# shellcheck disable=SC2034
UUID_SED='[0-9a-f]*-[0-9a-f]*-[0-9a-f]*-[0-9a-f]*-[0-9a-f]*'
# shellcheck disable=SC2034
ME=$(whoami)
MYIP=$(hostname -I | awk '{print $1}')

# -----------------------------------------------------------------------------
#
# EXIT
#
# -----------------------------------------------------------------------------

function echo_and_exit {
    if [[ $1 ]];then echo "$1"; shift; fi
    exit $1  # exit with error code  # TODO(reverse order, first code then str)
}
# shellcheck disable=SC2034
EXIT=echo_and_exit

# -----------------------------------------------------------------------------
#
# Platform
#
# -----------------------------------------------------------------------------

function is_cygwin {
    p=$(env|grep ^PATH=)
    if grep -q /cygdrive/c/WINDOWS <<< "$p"; then
        true
    else
        false
    fi
}

function is_admin {
    if is_cygwin; then
        if net session >/dev/null 2>&1; then true
        else false
        fi
    else
        if touch /root/test_${RANDOM} >/dev/null 2>&1; then true
        else false
        fi
    fi
}

function can_become_sudo {
    if is_cygwin; then
        if is_admin; then true
        else false
        fi
    else
	      true  # assumed
    fi
}

function SUDO {
    if is_cygwin; then
        if is_admin; then
            "$@"
        else
            debug "Can't execute [$*] as not being admin!"
        fi
    else
        sudo "$@"
    fi
}

if [[ ! $RM_PATH ]];then
# shellcheck disable=SC2209
RM_PATH=rm
fi
if [[ ! $CP_PATH ]];then
# shellcheck disable=SC2209
CP_PATH=cp
fi
if [[ ! $MV_PATH ]];then
# shellcheck disable=SC2209
MV_PATH=mv
fi

STDERR=/tmp/tmp.tmp

USE_LIGHT_COLOURS=1

if [[ $USE_LIGHT_COLOURS ]];then

RED='\033[0;91m'
GREEN='\033[0;92m'
YELLOW='\033[0;93m'
BLUE='\033[0;94m'
CYAN='\033[0;96m'

else

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'

fi

NC='\033[0m'  # no COLOUR

if [[ $NO_COLOR ]]; then
    # translate to british english
    echo "base.sh: WARN: please use NO_COLOUR, not NO_COLOR"
    NO_COLOUR=$NO_COLOR
fi


# -----------------------------------------------------------------------------
#
# console out
#
# -----------------------------------------------------------------------------

function out {
    if [[ ! $VERB ]]; then
        VERB='echo'
    fi
    $VERB "$*"
    unset VERB
}

function expressed_out {
    VERB='echo -e' out "$*"
}

function out_no_newline {
    VERB='echo -n' out "$*"
}

function expressed_out_no_newline {
    VERB='echo -e -n' out "$*"
}

function output {
    # silenceable
    if [[ $SILENT && ! $TWEET ]]; then
	      :
    else
        # shellcheck disable=SC1007
        out "$*"
	      unset TWEET  # TWEET unsilences only once
    fi
}

function expressed_output {
    VERB='echo -e' output "$*"
}

function output_no_newline {
    VERB='echo -n' output "$*"
}

function expressed_output_no_newline {
    VERB='echo -e -n' output "$*"
}

function start_colour {
    if [[ $NO_COLOUR ]]; then
        out_no_newline ''
    else
        expressed_out_no_newline "$COLOUR"
    fi
}

function end_colour {
    expressed_out_no_newline "$NC"
}

function coloured {
    if [[ $NO_COLOUR ]]; then
        out "$*"
    else
        expressed_out "$COLOUR$*$NC"
    fi
}

function coloured_no_newline {
    if [[ $NO_COLOUR ]]; then
        out_no_newline "$*"
    else
        expressed_out_no_newline "$COLOUR$*$NC"
    fi
}

function in_colour {
    # silenceable
    if [[ $NO_COLOUR ]]; then
        output "$*"
    else
        expressed_output "$COLOUR$*$NC"
    fi
}

function in_colour_no_newline {
    # silenceable
    if [[ $NO_COLOUR ]]; then
        output_no_newline "$*"
    else
        expressed_output_no_newline "$COLOUR$*$NC"
    fi
}

function start_red {
    # shellcheck disable=SC1007
    VERB= COLOUR=$RED start_colour
}

function red {
    # shellcheck disable=SC1007
    VERB= COLOUR=$RED coloured "$*"
}

function in_red {
    # silenceable
    # shellcheck disable=SC1007
    VERB= COLOUR=$RED in_colour "$*"
}

function red_no_newline {
    # shellcheck disable=SC1007
    VERB= COLOUR=$RED coloured_no_newline "$*"
}

function in_red_no_newline {
    # silenceable
    # shellcheck disable=SC1007
    VERB= COLOUR=$RED in_colour_no_newline "$*"
}

function start_green {
    # shellcheck disable=SC1007
    VERB= COLOUR=$GREEN start_colour
}

function green {
    # shellcheck disable=SC1007
    VERB= COLOUR=$GREEN coloured "$*"
}

function in_green {
    # silenceable
    # shellcheck disable=SC1007
    VERB= COLOUR=$GREEN in_colour "$*"
}

function green_no_newline {
    # shellcheck disable=SC1007
    VERB= COLOUR=$GREEN coloured_no_newline "$*"
}

function in_green_no_newline {
    # silenceable
    # shellcheck disable=SC1007
    VERB= COLOUR=$GREEN in_colour_no_newline "$*"
}

function start_yellow {
    # shellcheck disable=SC1007
    VERB= COLOUR=$YELLOW start_colour
}

function yellow {
    # shellcheck disable=SC1007
    VERB= COLOUR=$YELLOW coloured "$*"
}

function in_yellow {
    # silenceable
    # shellcheck disable=SC1007
    VERB= COLOUR=$YELLOW in_colour "$*"
}

function yellow_no_newline {
    # shellcheck disable=SC1007
    VERB= COLOUR=$YELLOW coloured_no_newline "$*"
}

function in_yellow_no_newline {
    # silenceable
    # shellcheck disable=SC1007
    VERB= COLOUR=$YELLOW in_colour_no_newline "$*"
}

function start_blue {
    # shellcheck disable=SC1007
    VERB= COLOUR=$BLUE start_colour
}

function blue {
    # shellcheck disable=SC1007
    VERB= COLOUR=$BLUE coloured "$*"
}

function in_blue {
    # silenceable
    # shellcheck disable=SC1007
    VERB= COLOUR=$BLUE in_colour "$*"
}

function blue_no_newline {
    # shellcheck disable=SC1007
    VERB= COLOUR=$BLUE coloured_no_newline "$*"
}

function in_blue_no_newline {
    # silenceable
    # shellcheck disable=SC1007
    VERB= COLOUR=$BLUE in_colour_no_newline "$*"
}

function cyan {
    # shellcheck disable=SC1007
    VERB= COLOUR=$CYAN coloured "$*"
}

function in_cyan {
    # silenceable
    # shellcheck disable=SC1007
    VERB= COLOUR=$CYAN in_colour "$*"
}

function cyan_no_newline {
    # shellcheck disable=SC1007
    VERB= COLOUR=$CYAN coloured_no_newline "$*"
}

function in_cyan_no_newline {
    # silenceable
    # shellcheck disable=SC1007
    VERB= COLOUR=$CYAN in_colour_no_newline "$*"
}

function do_red {
    start_red
    # shellcheck disable=SC2048
    $*
    end_colour
}

function do_green {
    start_green
    # shellcheck disable=SC2048
    $*
    end_colour
}

function do_yellow {
    start_yellow
    # shellcheck disable=SC2048
    $*
    end_colour
}

function do_blue {
    start_blue
    # shellcheck disable=SC2048
    $*
    end_colour
}

function do_cyan {
    start_cyan
    # shellcheck disable=SC2048
    $*
    end_colour
}

# colourful cats .. meow
function red_cat {
    do_red cat "$1"
}

function green_cat {
    do_green cat "$1"
}
function yellow_cat {
    do_yellow cat "$1"
}

function blue_cat {
    do_blue cat "$1"
}

function cyan_cat {
    do_cyan cat "$1"
}

# header
function green_characters {
    for _ in $(seq 1 "$1"); do
        green_no_newline "$2"
    done
    green
}

function header {
    num=${#1}
    green
    green_characters "$(( num + 6 ))" '='
    green
    green "   $1"
    green
    green_characters "$(( num + 6 ))" '='
    green
}

# -----------------------------------------------------------------------------
#
# logging
#
# -----------------------------------------------------------------------------

function error_info {
    red "-----"
    red "ERROR: $*"
    red "-----"
}

function warn {
    yellow "WARN: $*"
}

function info {
    yellow "$@"
}

function info_no_newline {
    yellow_no_newline "$@"
}

function debug {
    if [[ $TRACE_BASH ]]; then
        info "... TRACE: $*"
    elif [[ $DEBUG_BASH ]]; then
        info "... DEBUG: $*"
    fi
}

function debug_no_newline {
    if [[ $TRACE_BASH ]]; then
        info_no_newline "... TRACE: $*"
    elif [[ $DEBUG_BASH ]]; then
        info_no_newline "... DEBUG: $*"
    fi
}

# shellcheck disable=SC2120
function debug_blank {
    if [[ $TRACE_BASH || $DEBUG_BASH ]]; then
        info "$@"
    fi
}

function debug_blank_no_newline {
    if [[ $TRACE_BASH || $DEBUG_BASH ]]; then
        info_no_newline "$@"
    fi
}

function debug_eol {
    debug_blank
}

function debug_cat {
    if [[ $TRACE_BASH || $DEBUG_BASH ]]; then
        yellow_cat $1
    fi
}

function trace {
    if [[ $TRACE_BASH ]]; then
        yellow "... TRACE: $*"
    fi
}

# shellcheck disable=SC2120
function trace_blank {
    if [[ $TRACE_BASH ]]; then
        info "$@"
    fi
}

function trace_eol {
    trace_blank
}

function trace_cat {
    if [[ $TRACE_BASH ]]; then
        yellow_cat $1
    fi
}

function verbose {
    if [[ $VERBOSE || $TWEET || $DEBUG_BASH ]]; then
        # shellcheck disable=SC1007
        out "$*"
    fi
}

function expressed_verbose {
    VERB='echo -e' verbose "$*"
}

function coloured_verbose {
    # silenceable
    if [[ $NO_COLOUR ]]; then
        verbose "$*"
    else
        expressed_verbose "$COLOUR$*$NC"
    fi
}

function green_verbose {
    # silenceable
    # shellcheck disable=SC1007
    VERB= COLOUR=$GREEN coloured_verbose "$*"
}

function red_verbose {
    # silenceable
    # shellcheck disable=SC1007
    VERB= COLOUR=$RED coloured_verbose "$*"
}

function yellow_verbose {
    # silenceable
    # shellcheck disable=SC1007
    VERB= COLOUR=$YELLOW coloured_verbose "$*"
}

function blue_verbose {
    # silenceable
    # shellcheck disable=SC1007
    VERB= COLOUR=$BLUE coloured_verbose "$*"
}

function cyan_verbose {
    # silenceable
    # shellcheck disable=SC1007
    VERB= COLOUR=$CYAN coloured_verbose "$*"
}

function verbose_or_debug {
    if [[ $VERBOSE ]];then
        coloured "$@"
    else
        debug "$@"
    fi
}

function silent {
    if [[ ! $SILENT ]];then
        coloured "$@"
    fi
}

if [[ ! $WIN_AUDIO_STYLE_BASE ]]; then
    export FATAL_EXIT_BY_DEFAULT=1
fi

function error {
    if [[ $1 == '--fatal' ]];then
        fatal=1
        shift
    elif [[ $1 == '--noexit' || $1 == '--no-exit' ]];then
        # --- legacy, remove block ---
        if [[ $1 == '--noexit' ]];then
            warn "Please use --no-exit"
        fi
        warn "error: Please change to non-fatal by default"
        unset fatal
        shift
        # ------ end of legacy -------
    else
        if [[ $FATAL_EXIT_BY_DEFAULT ]];then
        fatal=1
        warn "error: Please change to non-fatal by default"
        else
        unset fatal
        fi
    fi
    error_info "$@"
    if [[ $fatal ]]; then exit; fi
}

function fatal_error {
    error --fatal "$@"
}

function error_cat {
    if [[ $1 == '--fatal' ]];then
        fatal=1
        shift
    elif [[ $1 == '--noexit' || $1 == '--no-exit' ]];then
        # --- legacy, remove block ---
        if [[ $1 == '--noexit' ]];then
            warn "Please use --no-exit"
        fi
        warn "error_cat: Please change to non-fatal by default"
        unset fatal
        shift
        # ==- end of legacy ---
    else
        if [[ $FATAL_EXIT_BY_DEFAULT ]];then
        fatal=1
        warn "error_cat: Please change to non-fatal by default"
        else
        unset fatal
        fi
    fi
    # shellcheck disable=SC2086
    red_cat $1
    if [[ $fatal ]]; then exit; fi
}


# -----------------------------------------------------------------------------
#
# Say something
#
# -----------------------------------------------------------------------------

debug "Sourcing base.sh"


# -----------------------------------------------------------------------------
#
# asserts
#
# -----------------------------------------------------------------------------

function assert_equal {
    if [[ $1 != "$2" ]]; then
        fatal_error "$1 != $2"
    fi
}

# -----------------------------------------------------------------------------
#
# redirect stderr
#
# -----------------------------------------------------------------------------

function r_stderr { if [[ $DEBUG_BASH ]]; then "$@"; else "$@" 2>/dev/null; fi; }

# -----------------------------------------------------------------------------
#
# Platform checks
#
# -----------------------------------------------------------------------------

function is_cbis() { if [[ $CBIS ]];then true; elif [[ -f ~/cbis/install_cbis_manager.py ]]; then red "Add export CBIS=1 to ~/.bashrc"; true; else false; fi; }
function check-cbis() { if is_cbis; then echo "Yes"; else echo "No"; fi; }
function is_shared_platform() { if is_cbis || [[ -f ~/stackrc || -f ~/overcloudrc ]]; then true; else false; fi; }
function check-shared-platform() { if is_shared_platform; then echo "Yes"; else echo "No"; fi; }
function on_overcloud() { if [[ $PS1 == *"overcloud"* ]];then true; else false; fi; }
function on-overcloud() { if on_overcloud; then echo "Yes"; else echo "No"; fi; }
function on_undercloud() { if [[ $PS1 == *"stackrc"* ]] || is_cbis && ! on_overcloud; then true; else false; fi; }
function on-undercloud() { if on_undercloud; then echo "Yes"; else echo "No"; fi; }

# -----------------------------------------------------------------------------
#
# Check packages and settings
#
# -----------------------------------------------------------------------------

function check_binary_exists {
    if [[ $1 ]];then
        binary=$1; if [[ $(which $binary 2>&1 >/dev/null| grep "no $binary") ]];then false; else true; fi
    else
        red "ERROR: Pass binary to check_binary_exists!"; false
    fi
}

function check_binary {
    if ! check_binary_exists "$1"; then
        echo "No support for $1 has been installed. Please rerun the script after installing."
        exit 1
    fi
}

# -----------------------------------------------------------------------------
#
# python and pprint
#
# -----------------------------------------------------------------------------

if check_binary_exists python; then
    PYTHON=python
elif check_binary_exists python2; then
    PYTHON=python2
elif check_binary_exists python3; then
    PYTHON=python3
else
    PYTHON=cant_do_this_there_is_no_python_on_this_system
fi

function pprint {
   echo "$1" | $PYTHON -mjson.tool
}

function pformat {
    # result=`pprint "$1"`
    pprint "$1"
}

function repeated_characters {
    for _ in $(seq 1 $1); do
        coloured_no_newline $2
    done
    coloured
}

function header {
    # use as:
    # IN_GREEN=1 header 'Collecting Logs'

    num=${#1}
    echo
    repeated_characters "$(( $num + 6 ))" '='
    echo
    coloured "   $1"
    echo
    repeated_characters "$(( $num + 6 ))" '='
    echo
}

# -----------------------------------------------------------------------------
#
# Console input
#
# -----------------------------------------------------------------------------

function ask {

    # shellcheck disable=SC2154
    ANSWER=$default

    unset POSITIVE

    echo -n "$@"

    if [[ $AUTO_PROCEED ]];then
    read -t $AUTO_PROCEED INPUT
    else
    read INPUT
    fi

    [ -n "$INPUT" ] && ANSWER=$INPUT

    if [[ $ANSWER == 'y' || $ANSWER == 'Y' || $ANSWER == 'yes' ]];then
        POSITIVE=1
    fi
}

function ask_default {
    ASK="$*"
    if [[ $AUTO_PROCEED ]];then
    ASK="$ASK (auto-proceeds in $AUTO_PROCEED secs)"
    fi
    if [[ $default == 'y' ]];then
    ASK="$ASK [Y|n] "
    else
    ASK="$ASK [N|y] "
    fi
    ask "$ASK"
}

function ask_default_yes {
    default=y ask_default "$@"
}

function ask_default_no {
    default=n ask_default "$@"
}

function caution_ask {
    echo -n -e "${RED}"
    ask_default_no "Caution: $*"
    echo -n -e "${NC}"
}

function proceed {
    echo "$1"
    AUTO_PROCEED=5 ask_default_yes "Proceed?"
    if [[ -z "$INPUT" ]];then echo "(y)"; fi
    if [[ ! $POSITIVE ]];then echo -e "${NC}Aborted!"; fi
}

function abort {
   ask_default_no "$1"
   if [[ ! $POSITIVE ]];then echo -e "${NC}Aborted!"; exit; fi

}

function triple_abort {
   echo -e "$YELLOW"

   abort "CAUTION! Are you SURE you want to $1?"
   abort "This will $1; are you POSITIVE?"
   abort "LAST WARNING: do you CONFIRM to $1?"

   echo -n -e "$NC"
}

function i_know_what_i_am_doing {
   if [[ $FORCE_SKIP_PRODUCTION_RUN_CONFIRM ]];then
      export SKIP_PRODUCTION_RUN_CONFIRM=1

   elif [[ ! $SKIP_PRODUCTION_RUN_CONFIRM ]];then
      triple_abort "$1"

      export SKIP_PRODUCTION_RUN_CONFIRM=1
   fi
}

function i_know_nothing {
   if [[ ! $FORCE_SKIP_PRODUCTION_RUN_CONFIRM ]];then

      yellow
      yellow "-- Safety measure -- set FORCE_SKIP_PRODUCTION_RUN_CONFIRM to avoid --"

      unset SKIP_PRODUCTION_RUN_CONFIRM
   fi

}

# -----------------------------------------------------------------------------
#
# dry-run
#
# -----------------------------------------------------------------------------

if [[ $DRY_RUN ]];then
    warn "DRY_RUN is obsolete! Use DRYRUN."
    DRYRUN=$DRY_RUN
fi

if [[ $HIGHLIGHTED_EMULATE ]];then
    EMULATE='yellow (dryrun)'
else
    EMULATE='echo (dryrun)'
fi

function dry_run {
    $EMULATE "$@"
}

function run {
    verbose "(run) $*"
    if [[ ! $NO_RUN ]];then
    if [[ $error_silent && ! $NO_ERROR_SILENT && ! $DEBUG_BASH ]];then
    "$@" 2> /dev/null
    else
    "$@"
    fi
    fi
}

function give_time_to_break_off {
    red_no_newline '    !Abort NOW if unintended! '
    for _ in {1..3}; do
        red_no_newline '.'
        sleep 1
    done
    echo -e '\n'
}

function act_for_dryrun_or_production {
    if [[ $DRYRUN ]];then
        DO=$EMULATE
        DRYRUN_TAG='(dryrun) '
    else
        DO=run  # ()
        # shellcheck disable=SC2034
        DRYRUN_TAG=''
    fi
}

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
#
if [[ $WIN_AUDIO_STYLE_BASE ]]; then
#
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# shellcheck disable=SC2120
function mark_dry_or_production_run {
    if [[ $PRODUCTION_RUN && ! $DRYRUN ]]; then
        if [[ $1 == '--production-run-must-be-verified' && ! $PRODUCTION_RUN_VERIFIED ]]; then
            error "PRODUCTION_RUN is set but PRODUCTION_RUN_VERIFIED is not."
            error "The run must be verified first."
            exit
        elif [[ $1 == '--production-run-must-be-run-as-admin' ]] && ! is_admin; then
            error "Must be run as administrator."
            exit
        fi
        red '*** THIS IS A PRODUCTION RUN! ***'
        give_time_to_break_off "$*"

    else  # PRODUCTION_RUN not set or DRYRUN set (taking precedence)
        # shellcheck disable=SC2034
        DRYRUN=1
        unset PRODUCTION_RUN
        green "*** DRY-RUN is ON ***"
        if [[ ! $SILENT ]]; then
            # green
            green "Set PRODUCTION_RUN for production run."
  	    fi
  	    if [[ $1 == '--production-run-must-be-run-as-admin' ]] && ! is_admin; then
  	        red "Mind, you must be admin to run this! (proceeding as dry-run)"
  	    fi
	      # green
    fi

    act_for_dryrun_or_production
}

# --------------------------------------------------------------------------- #
# Only use these options when you don't need to parse arguments.
# If you need to parse arguments, better parse them first; then, when good,
# give 'mark_dry_or_production_run'
# --------------------------------------------------------------------------- #

if [[ $1 == '--dryrun-as-default' ]];then
    mark_dry_or_production_run

elif [[ $1 == '--production-run-as-default' ]];then
    PRODUCTION_RUN=1
    mark_dry_or_production_run

# else , silently ignore; these may be options not meant for us
fi

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
#
else  # WIN AUDIO STYLE BASE
#
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

if [[ $THIS_MODULE_COMES_AS_DRYRUN_BY_DEFAULT ]];then

    if [[ ! $PRODUCTION_RUN ]];then

    DRYRUN=1

    if [[ ! $SKIP_DRYRUN_ANNOUNCEMENT ]];then
    green "Dry-run is on!"
    green "For production run, give:"
    green "    export PRODUCTION_RUN=1"
    fi

    elif [[ ! $SKIP_PRODUCTION_RUN_CONFIRM ]];then

    warn "This is not a drill! This is a production run."
    read -p "Please confirm [Y] (give ctrl-C to abort)"

    fi

    act_for_dryrun_or_production

elif [[ $DRYRUN && ! $PRODUCTION_RUN ]];then

    DRYRUN=1

    if [[ ! $SKIP_DRYRUN_ANNOUNCEMENT ]];then
    green "Dry-run is on!"
    green "Unset DRYRUN, or give:"
    green "    export PRODUCTION_RUN=1"
    fi

    act_for_dryrun_or_production

elif [[ ! $DRYRUN && $PRODUCTION_RUN ]];then

    if [[ ! $SKIP_PRODUCTION_RUN_CONFIRM ]];then

    warn "This is not a drill! This is a production run."
    read -p "Please confirm [Y] (give ctrl-C to abort)"

    fi

    act_for_dryrun_or_production

elif [[ $DRYRUN && $PRODUCTION_RUN ]];then

    error "Both DRYRUN and PRODUCTION_RUN are defined; unset one of both."

fi

function production_run_confirm {

if [[ $PRODUCTION_RUN && ! $SKIP_PRODUCTION_RUN_CONFIRM ]];then
    warn "Again, this is not a drill! $1"
    read -p "Please confirm [Y] (give ctrl-C to abort)"

    echo
    green "INITIATING PRODUCTION RUN"
    green "-------------------------"
fi

}

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
#
fi   # WIN AUDIO STYLE BASE
#
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#
# execution
#
# -----------------------------------------------------------------------------

function _execute {
    out=
    err=
    $RM_PATH -f $STDERR

    if [[ $COLOURED_OUT ]];then
        if [[ $redirect_all ]];then
            blue "> $* [redirect-all]"
        elif [[ $error_silent ]];then
            blue "> $* [error-silent]"
        else
            blue "> $*"
        fi
    fi
    if [[ $LIVE_EXECUTE ]];then

        if [[ $redirect_all ]];then
            error "LIVE_EXECUTE and redirect_all combo is not supported"

        elif [[ $error_silent && ! $DEBUG_BASH ]];then
            if [[ $TRACE_BASH ]];then
                "$@"
            elif [[ $SILENT ]];then
                err=$STDERR
                "$@" >/dev/null 2>$err
            else
                err=$STDERR
                "$@" 2>$err
            fi

        elif [[ $error_silent && $DEBUG_BASH ]];then
            if [[ $SILENT ]];then
                "$@" >/dev/null 2>/dev/null
            else
                "$@" 2>/dev/null
            fi

        elif [[ ! $TRACE_BASH && $SILENT ]];then
            "$@" >/dev/null
        else
            "$@"
        fi

    elif [[ $redirect_all ]];then
        err=$STDERR
        out=$("$@" &>$err)

    else
        if [[ $error_intolerant ]];then
            out=$("$@" 2>$STDERR)
            if [[ -s $STDERR ]];then
                error_cat $STDERR
            fi

        elif [[ $error_silent || $TRACE_BASH || ($DEBUG_BASH || $VERBOSE) && ! $SILENT ]];then
            err=$STDERR
            out=$("$@" 2>$err)

        else
            out=$("$@")
        fi
    fi

    if [[ $err && ! -f $err ]];then
        # weird..... but occasionally happens
        err=
    fi
}

function filtered {
    if [[ $grep_filter1 && ! $grep_filter2 ]];then
        # shellcheck disable=SC2154
        debug "$* | grep $grep_filter1_options $grep_filter1"
        _execute "$@"
        # WARN: DO NOT quote the grep filters
        out=$(echo "$out"| grep $grep_filter1_options $grep_filter1)
    elif [[ $grep_filter1 && ! $grep_filter3 ]];then
        # shellcheck disable=SC2154
        debug "$* | grep $grep_filter1_options $grep_filter1| grep $grep_filter2_options $grep_filter2"
        _execute "$@"
        # WARN: DO NOT quote the grep filters
        out=$(echo "$out"| grep $grep_filter1_options $grep_filter1| grep $grep_filter2_options $grep_filter2)
    elif [[ $grep_filter1 ]];then
        # shellcheck disable=SC2154
        debug "$* | grep $grep_filter1_options $grep_filter1| grep $grep_filter2_options $grep_filter2| grep $grep_filter3_options $grep_filter3"
        _execute "$@"
        # WARN: DO NOT quote the grep filters
        out=$(echo "$out"| grep $grep_filter1_options $grep_filter1| grep $grep_filter2_options $grep_filter2| grep $grep_filter3_options $grep_filter3)

    elif [[ $awk_filter1 && ! $awk_filter2 ]];then
        debug "$* | awk $awk_filter1"
        _execute "$@"
        out=$(echo "$out"| awk "$awk_filter1")
    elif [[ $awk_filter1 && ! $awk_filter3 ]];then
        debug "$* | awk $awk_filter1| awk $awk_filter2"
        _execute "$@"
        out=$(echo "$out"| awk "$awk_filter1"| awk "$awk_filter2")
    elif [[ $awk_filter1 ]];then
        debug "$* | awk $awk_filter1| awk $awk_filter2| awk $awk_filter3"
        _execute "$@"
        out=$(echo "$out"| awk "$awk_filter1"| awk "$awk_filter2"| awk "$awk_filter3")

    else
        echo "ERROR: no filter set"
        exit 1
    fi

    grep_filter1=
    grep_filter2=
    grep_filter3=

    awk_filter1=
    awk_filter2=
    awk_filter3=

}

function execute {
    # if cached is set and $out defined, it does not update $out
    if [[ -z $cached || -z $out ]]; then

        $RM_PATH -f $STDERR
        out=
        err=

        error_silent_set=$error_silent
        redirect_all_set=$redirect_all

        if [[ $echo_out ]];then
            redirect_all=1
        fi

        if [[ $SILENT || $error_tolerant ]];then
            error_silent=1  # if silent then also error-silent
        fi

        if [[ $redirect_all ]];then
            error_silent=1  # if redirect_all then also error-silent
        fi

        if [[ $DRYRUN && ! $THIS_IS_SAFE ]];then
            $EMULATE "$*"

        elif [[ $grep_filter1 || $awk_filter1 ]];then
            filtered "$@"

        else
            debug "$@"
            _execute "$@"
        fi

        if [[ $err && $(grep -v deprecated $err) ]];then
            if [[ $ALWAYS_REPORT_ERRORS && ! $error_tolerant ]];then
                red_cat "$err"
            fi
            if [[ $COLOURED_OUT ]];then
                if [[ $redirect_all ]];then
                    # cannot diff between out and err
                    blue_cat "$err"
                else
                    red_cat "$err"
                fi
            fi
            if [[ $TRACE_BASH ]];then
                trace ">>"
                trace_cat "$err"
            elif [[ ! $error_silent && $DEBUG_BASH ]];then
                debug ">>"
                debug_cat "$err"
            elif [[ ! $error_silent && $VERBOSE && ! $SILENT ]];then
                cat "$err"
            fi
        fi

        if [[ $out ]];then
            if [[ $COLOURED_OUT && ! $redirect_all ]];then
                blue "$out"
            fi
            if [[ $VERBOSE && ! $SILENT ]];then
                if [[ $DISPLAY_ID_ONLY ]];then
                    out_id=$(echo "$out" | grep -w id | grep -E -o $UUID)
                    echo "(reducing output) (id = $out_id)"
                else
                    echo "$out"
                fi
            elif [[ $TRACE_BASH ]];then
                trace ">\n$out"
            elif [[ ! $SILENT ]];then
                debug ">\n$out"
            fi
        elif [[ ! $LIVE_EXECUTE ]];then
            trace "> (empty)"
        fi

        if [[ $echo_out ]];then
            if [[ $out ]];then
                green "$out"
            fi
            if [[ -s $STDERR ]];then
                green_cat $STDERR
            fi
        fi

        redirect_all=$redirect_all_set
        error_silent=$error_silent_set

    fi
}

function safe_execute {
    THIS_IS_SAFE=1 execute "$@"
}

function live_execute {
    LIVE_EXECUTE=1 execute "$@"
}

function live_safe_execute {
    LIVE_EXECUTE=1 safe_execute "$@"
}

# -----------------------------------------------------------------------------
#
# execution, alternative style
#
# -----------------------------------------------------------------------------

function give {
    debug "$@"
    $DO "$@"
}

# -----------------------------------------------------------------------------
#
# openstack
#
# -----------------------------------------------------------------------------

function _give_os {
    if [[ $DRYRUN ]];then
        $EMULATE "$@"

    else
        yellow "$@"
        ERROR=$("$@" 2>&1 >/dev/null | grep -v deprecated)

        if [[ $ERROR ]];then
            red "ERROR: $ERROR"
        fi
    fi
}

function give_openstack {
    _give_os "openstack $*"
}

function give_nova {
    _give_os "nova $*"
}

function give_neutron {
    _give_os "neutron $*"
}

function os_run {
    if [[ $VERBOSE ]];then
        yellow "$@"
    fi
    error_silent=1 execute "$@"
    id=$(echo "$out" | grep -E "^\| id " | grep -E -o $UUID)

    if [[ $VERBOSE && $id ]];then
        green "id = $id"
    fi
}

# -----------------------------------------------------------------------------
#
# remote execution
#
# -----------------------------------------------------------------------------

# use as :
# SSH secret jeremy@host [cmd_or_options]
function SSH() {
    pass="$1"
    user_at_host="$2"
    cmd_or_options="$3"

    debug "SSH $*"

    error_silent=$error_silent $DO sshpass -p "$pass" ssh -o StrictHostKeyChecking=no -t "$user_at_host" "$cmd_or_options"
}

# use as:
# SCP $INFRA_PASS clean_tap_itfs.sh infra@aninfra-noc-compute92 ~
function SCP() {
    pass="$1"
    path="$2"
    user_at_host="$3"
    target_path="$4"

    debug "SCP $*"

    if [[ ! $target_path ]];then target_path="$path"; fi

    error_silent=$error_silent $DO sshpass -p "$pass" scp -o StrictHostKeyChecking=no "$path" "$user_at_host":"$target_path"
}

function SCP_R() {
    pass="$1"
    path="$2"
    user_at_host="$3"
    target_path="$4"

    debug "SCP_R $*"

    if [[ ! $target_path ]];then target_path="$path"; fi

    error_silent=$error_silent $DO sshpass -p "$pass" scp -o StrictHostKeyChecking=no -r "$path" "$user_at_host":"$target_path"
}

# use as:
# exec-at homer password server "mkdir ~/dev/ollekebolleke"
function exec-at {
    whom="$1"
    pass="$2"
    server="$3"
    cmd="$4"

    error_silent=$error_silent SSH "$pass" "$whom@$server" "$cmd"
}

function remote_mkdir {
    whom="$1"
    pass="$2"
    server="$3"
    dir="$4"

    if [[ $LOCAL ]]; then
    green "Locally creating $dir"
    $DO mkdir -p "$dir"

    else
    green "Remotely creating $dir"

    # shellcheck disable=SC1003
    dir=${dir//\'/\'\"\'\"\'}  # escape ' with '"'"'

    # error silent for not getting "Connection to ... closed." message
    exec-at "$whom" "$pass" "$server" "mkdir -p '$dir'"
    fi
}

# use as:
# scp-to homer password server ~/dev/ollekebolleke/index.html
function scp-to {
    whom="$1"
    pass="$2"
    server="$3"
    path="$4"
    target_path="$5"

    error_silent=$error_silent SCP "$pass" "$path" "$whom@$server" "$target_path"
}

function scp-r-to {
    whom="$1"
    pass="$2"
    server="$3"
    path="$4"
    target_path="$5"

    error_silent=$error_silent SCP_R "$pass" "$path" "$whom@$server" "$target_path"
}

function scp_dir {
    whom="$1"
    pass="$2"
    server="$3"
    src="$4"
    dst="$5"

    if [[ ! $dst ]];then
        dst="$src"
    fi
    if [[ $LOCAL ]]; then
        green "Locally copying $src"
        $DO cp "$dst" "/tmp$dst"

    else
        green "Remotely copying $src"
        dst=${dst// /\\\ }  # escape spaces with triple-backslash
        # shellcheck disable=SC1003
        dst=${dst//\'/\\\'}  # escape ' with triple-backslash
        dst=${dst//\(/\\\(}  # escape ( with triple-backslash
        dst=${dst//\)/\\\)}  # escape ) with triple-backslash

        scp-r-to "$whom" "$pass" "$server" "$src" "$dst"
    fi
}

function scp_file {
    whom="$1"
    pass="$2"
    server="$3"
    src="$4"
    dst="$5"

    if [[ ! $dst ]];then
        dst="$src"
    fi
    if [[ $LOCAL ]]; then
        green "Locally copying $src"
        $DO cp "$dst" "/tmp$dst"

    else
        green "Remotely copying $src"
        dst=${dst// /\\\ }  # escape spaces with triple-backslash
        # shellcheck disable=SC1003
        dst=${dst//\'/\\\'}  # escape ' with triple-backslash
        dst=${dst//\(/\\\(}  # escape ( with triple-backslash
        dst=${dst//\)/\\\)}  # escape ) with triple-backslash

        scp-to "$whom" "$pass" "$server" "$src" "$dst"
    fi
}

# -----------------------------------------------------------------------------
#
# file system
#
# -----------------------------------------------------------------------------

function check_dir_exists {
    if [[ -d $1 ]]; then true
    else false
    fi
}

function makedir {
   if [[ ! -d $1 ]];then
       $DO mkdir $1
   fi
}

function check_dir_non_empty {
    if ! check_dir_exists "$1"; then false
    elif [[ ! $(ls "$1") ]]; then false
    else true
    fi
}

function assert_non_empty_dir {
    if ! check_dir_non_empty "$1"; then
        fatal_error "$1 is empty"
    fi
}

function copy {
   src_file=$1
   new_dir=$2
   new_file=$(echo "$src_file" | rev | cut -d"/" -f1 | rev)

   if [[ ! -f "$new_dir/$new_file" ]];then
       $DO cp $src_file $new_dir
   fi
}

function does_file_exist_with_wildcard {
   local arg="$*"
   local files=($arg)
   [ ${#files[@]} -gt 1 ] || [ ${#files[@]} -eq 1 ] && [ -e "${files[0]}" ]
}

# -----------------------------------------------------------------------------
#
# other
#
# -----------------------------------------------------------------------------

function sequence {
    seq=
    for i in "$@"; do
        if [[ $seq ]];then
            seq="$seq $i"
        else
            seq="$i"
        fi
    done
}

function check_is_set {
    # ${!varname} resolves the variable named varname
    if [[ ${!1} ]];then
        debug "$1=${!1}"
    else
        echo "Error: $"$1" is not set!"
        exit 1
    fi
}

function swap {
    # ${!varname} resolves the variable named varname
    TMP="${!1}"
    eval $1="${!2}"
    eval $2="$TMP"
}

function os_info {
    if [[ $CYG_SYS_BASHRC ]];then
        DISTRO='Cygwin'
        # shellcheck disable=SC2034
        CYGWIN=1

    elif [[ -f /etc/os-release ]];then
        DISTRO=$(awk -F= '/^NAME/{print $2}' /etc/os-release)
    else
        echo "WHAT platform are YOU on!?"
    fi

    # shellcheck disable=SC2034
    if [[ ${DISTRO} =~ 'Ubuntu' ]]; then
        DISTRO='Ubuntu'
        UBUNTU=1
        OS="$DISTRO "`lsb_release -a 2>/dev/null | grep "Description" | grep -o -E "[0-9]*\..*"`

    elif [[ ${DISTRO} =~ 'CentOS' ]]; then
        DISTRO='CentOS'
        CENTOS=1
        if [[ $(grep "Stream" /etc/centos-release) ]];then
            OS=$(cat /etc/centos-release)
        else
            OS="$DISTRO "`cat /etc/centos-release| grep -E -o "[0-9]*\..*"`
        fi

    elif [[ ${DISTRO} =~ 'Red Hat Enterprise Linux Server' ]]; then
        DISTRO='RHEL'
        RHEL=1
        OS="$DISTRO "$(cat /etc/redhat-release| grep -E -o "[0-9]*\..*")
    fi

    if [[ $VERBOSE || $1 == '--verbose' ]];then echo "On $OS"; fi

}

function add_ip_to_hosts {
    debug "add_ip_to_hosts invoked..."
    if can_become_sudo; then
	      if [[ ! $(grep $MYIP /etc/hosts) ]]; then
            debug "Updating /etc/hosts"
            echo "$MYIP" $(hostname) | SUDO tee -a /etc/hosts 1>/dev/null 2>/dev/null
        fi
    else
	      debug "Skipping, can't become sudo"
    fi
}

function check_settings {
    if [[ $DRYRUN ]];then
        echo
        echo "DRYRUN exection is set"
        echo "Disable it by:"
        echo "unset DRYRUN"
    else
        echo
        echo "Enable DRYRUN execution by:"
        echo "export DRYRUN=1"
    fi

    if [[ $DEBUG_BASH ]];then
        echo
        echo "DEBUG_BASH is set"

        if [[ $TRACE_BASH ]];then
            echo "TRACE_BASH is set"
        fi

    elif [[ $TRACE_BASH ]];then
        echo
        echo "TRACE_BASH is set"
    fi

    if [[ $TRACE_BASH ]];then
        echo
        echo "Disable trace by:"
        echo "unset TRACE_BASH"

    else
        if [[ $DEBUG_BASH ]];then
            echo
            echo "Disable debug by:"
            echo "unset DEBUG_BASH"
        else
            echo
            echo "Enable debug by:"
            echo "export DEBUG_BASH=1"
        fi
        echo
        echo "Enable trace by:"
        echo "export TRACE_BASH=1"

    fi

}

function openstack-version {
    if [[ -f /opt/stack/nuage-openstack-neutron/tox.ini ]];then
        version=$(grep -E -o upper-constraints.txt.[a-z?=/]* /opt/stack/nuage-openstack-neutron/tox.ini)
        if [[ $version == *stable/* ]];then
            version=$(echo $version|grep -E -o stable.*)
        else
            version=master
        fi
        if [[ $1 != '--silent' ]];then
            echo $version
        fi
    else
        red "ERROR: Cannot determine openstack-version!"
        version=boutrosboutrosgali
    fi
}

function sudo_pip_install {
    ARGS="$*"
    if [[ $DONT_SATISFY_UPPER_CONSTRAINTS && -f /opt/stack/requirements/upper-constraints.txt ]];then
        red "WARN: NOT satifying /opt/stack/requirements/upper-constraints.txt"
    elif [[ ! $DONT_SATISFY_UPPER_CONSTRAINTS && -f /opt/stack/requirements/upper-constraints.txt ]];then
        ARGS="-c /opt/stack/requirements/upper-constraints.txt $ARGS"
    fi
    sudo -HE pip install $ARGS
}

function sudo_pip3_install {
    ARGS="$*"
    if [[ $DONT_SATISFY_UPPER_CONSTRAINTS && -f /opt/stack/requirements/upper-constraints.txt ]];then
        red "WARN: NOT satifying /opt/stack/requirements/upper-constraints.txt"
    elif [[ ! $DONT_SATISFY_UPPER_CONSTRAINTS && -f /opt/stack/requirements/upper-constraints.txt ]];then
        ARGS="-c /opt/stack/requirements/upper-constraints.txt $ARGS"
    fi
    sudo -HE pip3 install $ARGS
}


# --- on uc node, swap between uc and oc ---

function to_undercloud {
    if [[ -f ~/stackrc ]];then

        CLOUDPROMPT_ENABLED=1 . ~/stackrc

        if [[ $1 == '--verbose' ]];then
            green "stackrc sourced"

        elif [[ $1 == '--extra-verbose' ]];then
            green "stackrc sourced ($OS_AUTH_URL)"

        else
            debug "stackrc sourced"
        fi

    else

        warn "No ~/stackrc found!"

    fi
}

function to_overcloud {
    if [[ -f ~/overcloudrc ]];then

        CLOUDPROMPT_ENABLED=1 . ~/overcloudrc

        if [[ $1 == '--verbose' ]];then
            green "overcloudrc sourced"

        elif [[ $1 == '--extra-verbose' ]];then
            green "overcloudrc sourced ($OS_AUTH_URL)"

        else
            debug "overcloudrc sourced"
        fi

    # else
    #     warn "No ~/overcloudrc found!"

    fi
}

# -----------------------------------------------------------------------------
#
# GIT
#
# -----------------------------------------------------------------------------

# shellcheck disable=SC2034
GIT='execute git'  # GIT will yield to void in dry-run mode
# shellcheck disable=SC2034
SAFE_GIT='safe_execute git'  # SAFE_GIT will remain exec'ing git in dry-run mode(!)


# -----------------------------------------------------------------------------
#
# Remote execution
#
# -----------------------------------------------------------------------------

function quick-ping { if [[ $(/usr/bin/ping -w 1 -W 1 -c 1 $1 | grep '1 packets received') ]]; then if [[ $VERBOSE ]];then echo "Successfully pinged $1"; fi; true; else red "Can't reach $1"; false; fi; }

function cp_file {
    target=$1
    file=$2
    pass=$3
    sshpass -p $pass scp -o StrictHostKeyChecking=no $file infra@$target:~
}

function _exec_file {
    debug "exec_file $*"
    target=$1
    shift
    file=$1
    shift
    pass=$1
    shift
    cp_file $target $file $pass
    sshpass -p $pass ssh -o StrictHostKeyChecking=no -t infra@$target "chmod +x $file; $SUDO ./$file $*; rm $file"
}

function exec_file {
    SUDO=
    _exec_file "$@"
}

function exec_file_as_sudo {
    SUDO='sudo'
    _exec_file "$@"
}

# -----------------------------------------------------------------------------
#
# Go remote
#
# -----------------------------------------------------------------------------

WF_BED=wfdcvtb01.wf.nuagenetworks.net
WF_USER=wfdcvtb01
WF_PASS=$NUAGE_PASS

WF_JENKINS=wfnursync.wf.nuagenetworks.net  # wfnujenkins.wf.nuagenetworks.net
WF_JENKINS_USER=infra
WF_JENKINS_PASS=$INFRA_PASS

function _set_remotes {

    if [[ $COPY_FROM_JENKINS ]];then
    if [[ ! $INFRA_PASS ]];then
        echo "You need INFRA_PASS to be set, sorry."
        exit 1
    fi
    USER=$WF_JENKINS_USER
    PASS=$WF_JENKINS_PASS
    SERVER=$WF_JENKINS
    else
    USER=$WF_USER
    PASS=$WF_PASS
    SERVER=$WF_BED
    fi
}

function copy_from_wf {

    _set_remotes

    SRC=$1
    DST=$2

    debug "copy_from_wf $SRC $DST"

    live_execute sshpass -p $PASS scp -o StrictHostKeyChecking=no $USER@$SERVER:$SRC $DST

    debug "copy complete!"
}

# --
# Use this when you don't want path+file to be resolved on the local file system (!)
# --
function copy_from_wf_by_path {

    _set_remotes

    SRCPATH=$1
    SRCFILE=$2
    DST=$3

    debug "copy_from_wf $SRCPATH/$SRCFILE to $DST"

    live_execute sshpass -p $PASS scp -o StrictHostKeyChecking=no $USER@$SERVER:$SRCPATH/$SRCFILE $DST

    debug "copy complete!"
}

# -----------------------------------------------------------------------------
#
# Gimmicks
#
# -----------------------------------------------------------------------------

function get_antwerp_date_and_time {

    date_and_time="It is "$(date +%A)", "$(date +%e)"th of "$(date +%B)" and "$(date +%H:%M:%S)" in Antwerp currently.\n"

}

function get_antwerp_time_and_weather {

    weather=$(curl wttr.in/Antwerp?0Q 2>/dev/null)
    if [[ ! $weather || $(echo $weather|grep "500 Internal Server Error") ]];then
    red "There is currently no weather report."
    current=
    time_and_weather=
    else
    current=$(echo "$weather" | head -1 | grep -o -E "[A-Z].*"| tr '[:upper:]' '[:lower:]')
    time_and_weather="It is currently "$(date +%H:%M:%S)" and $current in Antwerp.\n\n$weather\n"
    fi

}

function print_antwerp_date_and_time {

    get_antwerp_date_and_time
    if [[ "$date_and_time" ]];then
    yellow "$date_and_time"
    fi

}

function print_antwerp_time_and_weather {

    get_antwerp_time_and_weather
    if [[ "$time_and_weather" ]];then
    yellow "$time_and_weather"
    fi

}

# -----------------------------------------------------------------------------
#
# Print utils
#
# -----------------------------------------------------------------------------

function repeat () {
    what=$1
    count=$2
    seq $count | xargs -n 1 | xargs -I {} echo -n $what;echo
}

# -----------------------------------------------------------------------------
#
# OpenStack utils
#
# -----------------------------------------------------------------------------

function vm-ip { nova list --all 2>/dev/null| grep -E "$1 *\|" | grep -o -E "$IP" ; }
function noc-vm-ip { if [[ $1 == "10.40."* ]];then echo $1; else openstack server show $1 2>/dev/null|grep addresses|grep -E -o "10\.40\.[0-9]*\.[0-9]*"; fi; }
function vm-uuid { uuid=$(echo "$1"| grep -o -E "$UUID"); if [[ $uuid ]];then echo $uuid; else nova list --all 2>/dev/null | grep "$1 " | grep -o -E "| $UUID" | grep -o -E "$UUID"; fi; }
function vm-show { openstack server show $(vm-uuid $1) $2 $3 $4 $5 2>/dev/null; }
function vm-attribute { vm-show $1 -c $2 -f value; }
function vm-compute { vm-attribute $1 OS-EXT-SRV-ATTR:hypervisor_hostname; }
function vm-instance { vm-attribute $1 OS-EXT-SRV-ATTR:instance_name; }

# -----------------------------------------------------------------------------
#
# end of script
#
# -----------------------------------------------------------------------------

function end_of_script {
     echo
     $RM_PATH -f $STDERR
}


# ----- finally, finish off -----

debug "Sourcing base.sh complete"

IN_GREEN=1 verbose "Verbose is ON"

if [[ $SILENT ]];then
    debug "Silent is ON"
fi

BASE_SH_SOURCED=1


# -----------------------------------------------------------------------------
#
#                                END OF SCRIPT
#
# -----------------------------------------------------------------------------


else

debug "Did not re-source as BASE_SH_SOURCED was set"

fi
