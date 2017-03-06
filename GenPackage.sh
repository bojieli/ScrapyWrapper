#!/bin/sh
python2 -m compileall -f .
find . -type f -name '*.py' -exec rm -f {} \;
