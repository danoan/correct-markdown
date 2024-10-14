#! /usr/bin/env bash

SCRIPT_FOLDER="$( cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INPUT_FOLDER="${SCRIPT_FOLDER}/input"
OUTPUT_FOLDER="${SCRIPT_FOLDER}/output"
mkdir -p "${OUTPUT_FOLDER}"

PROJECT_FOLDER="$(cd "${SCRIPT_FOLDER}" && cd .. && pwd)"

pushd "${PROJECT_FOLDER}/src/danoan/correct_markdown/core" > /dev/null
python -m doctest string_view.py
popd > /dev/null

pushd "${PROJECT_FOLDER}/docs" > /dev/null
python -m doctest *.md -o NORMALIZE_WHITESPACE
popd > /dev/null
