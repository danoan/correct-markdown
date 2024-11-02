#! /usr/bin/env bash

SCRIPT_FOLDER="$( cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INPUT_FOLDER="${SCRIPT_FOLDER}/input"
OUTPUT_FOLDER="${SCRIPT_FOLDER}/output"
mkdir -p "${OUTPUT_FOLDER}"

MAKEFILE_FOLDER="$(cd "${SCRIPT_FOLDER}" && cd ../.. && pwd)"
pushd "${MAKEFILE_FOLDER}" > /dev/null


make BUILD_FOLDER=${SCRIPT_FOLDER}/build MARKDOWN_FILE=${SCRIPT_FOLDER}/arnaud.md LANGUAGE=french TITLE=Arnaud
# make BUILD_FOLDER=${SCRIPT_FOLDER}/build MARKDOWN_FILE=${SCRIPT_FOLDER}/arnaud.md LANGUAGE=french TITLE=Arnaud ${SCRIPT_FOLDER}/build/arnaud/render-data.json

make -Bnd BUILD_FOLDER=${SCRIPT_FOLDER}/build MARKDOWN_FILE=${SCRIPT_FOLDER}/arnaud.md LANGUAGE=french TITLE=Arnaud | ~/Sources/makefile2graph/make2graph > out.dot
dot out.dot -Tpng -o out.png

popd > /dev/null
