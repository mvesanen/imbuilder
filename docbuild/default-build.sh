#!/usr/bin/env bash
set -e
set -u
set -o pipefail



here=$(cd $(dirname $0); pwd -P)
cd $here

echo "Prosessing intermediate markdown ..."
time python ./raw-parse.py $1
echo
echo "Generating documents ..."

cp ./staging/figures/logo/* ./
cp ./staging/figures/logo/* ./staging

time python ./pandoc.py staging/$(basename $1)

ls ./artefact

mkdir ../git/artefact

cp ./artefact/* ../git/artefact
cp ./staging/main.md ../git/artefact/inframodel.md

