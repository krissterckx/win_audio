#!/bin/bash

. __lib/functions.sh

if check_drive; then
    green "The drive is connected"
else
    yellow "The drive is not connected"
fi
