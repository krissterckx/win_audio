#!/bin/bash
# just a little thingy

. __lib/functions.sh

re='^[0-9]+$'

DAYS=$1
if [[ ! $DAYS ]];then
DAYS=1
fi

if [[ $1 == '-h' || $1 == '--help' || ! $DAYS =~ $re || $2 ]];then
echo "Use as:"
echo "    $0 [days count]"
echo
exit
fi

cd "$MUSIC" || exit

if [[ $DAYS == '1' ]];then
green "Checking $PWD for changes within the last day..."
else
green "Checking $PWD for changes within the last $DAYS days..."
fi
green

find . -mtime -$DAYS -type f -print | grep -v ".ini"
