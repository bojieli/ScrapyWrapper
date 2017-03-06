#!/bin/bash
cd $(dirname $0)
SCRIPT="$1"
[ ! -f "${SCRIPT}.py" ] && [ ! -f "${SCRIPT}.pyc" ] && echo "Neither script ${SCRIPT}.py nor compiled script ${SCRIPT}.pyc was found" && exit 1
if [ -f "${SCRIPT}.py" ]; then
	SCRIPTFILE="${SCRIPT}.py"
else
	SCRIPTFILE="${SCRIPT}.pyc"
fi
LOGDIR=logs
LOGSUBDIR=$SCRIPT
mkdir -p $LOGDIR/$LOGSUBDIR
LOGFILE=$LOGDIR/$LOGSUBDIR/$(date '+%Y-%m-%d').log
export PATH=$PATH:/usr/local/bin
/usr/local/bin/scrapy runspider ${SCRIPTFILE} >$LOGFILE 2>&1
exit 0
