#!/bin/bash
# Rückfalltest: spielt alle Handy-Aufnahmen mit einer App-Datei nach und gibt die Gegenprobe je Aufnahme aus.
# usage: tools/bench/regress.sh APP.html [DIAGDIR=/tmp/diagrepo]    (APP.html = web/index.html oder eine Testkopie)
APP=$(readlink -f "$1"); ROOT=${2:-/tmp/diagrepo}; HERE=$(cd "$(dirname "$0")" && pwd); TMP=$(mktemp -d)
for d in $ROOT/*_done; do
  W=$TMP/$(basename $d); mkdir -p $W; cp $d/rec.json $d/meta.json $W/; cp $d/*.jpg $W/ 2>/dev/null
  (cd $HERE && DIAG_APP=file://$APP python3 -c "import diag,sys;diag.replay(sys.argv[1])" $W >/dev/null 2>&1)
  echo "$(basename $d | cut -c12-45) | $(python3 $HERE/gegenprobe.py $d $W/replay-notes.json 2>&1 | cut -c1-120)"
done
