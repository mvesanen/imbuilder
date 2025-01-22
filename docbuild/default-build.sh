#!/usr/bin/env bash
set -e
set -u
set -o pipefail



here=$(cd $(dirname $0); pwd -P)
cd $here

echo "Prosessing intermediate markdown ..."
time python ./raw-parse.py $1 $4
echo
echo "Generating documents ..."

cp ./staging/figures/logo/* ./
cp ./staging/figures/logo/* ./staging

if [ "$#" -gt 1 ]; then
    time python ./pandoc.py staging/$(basename $1)

    time python ./schemaprocessor.py $2 ./artefact/$3

    ls ./artefact
fi
cp ./artefact/* ../git/artefact
cp ./staging/main.md ../git/artefact/inframodel.md

