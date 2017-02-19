#!/bin/bash
cd $(dirname $0)
SCRIPT=$1
[ ! -f "${SCRIPT}.py" ] && echo "script ${SCRIPT}.py not found" && exit 1
LOGDIR=logs
LOGSUBDIR=$SCRIPT
mkdir -p $LOGDIR/$LOGSUBDIR
LOGFILE=$LOGDIR/$LOGSUBDIR/$(date '+%Y-%m-%d').log
scrapy runspider ${SCRIPT}.py >$LOGFILE 2>&1
exit 0