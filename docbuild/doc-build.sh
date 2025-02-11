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

time python ./pandoc-gen.py staging/$(basename $1) $2

# time python ./schemaprocessor.py $2 ./artefact/$3

# ls ./artefact

cp ./artefact/* ../git/artefact
#cp -r /docbuild/staging/* ../git/staging
#cp ./staging/$(basename $1) ../git/artefact/output.md

