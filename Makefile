# Given a markdown file, it does the following:
# 1. Find errors in the text and generates a corrected version;
# 2. All the corrections are collected and passed to a prompt to explain why they were made;
# 3. Bold-faced words are collected and a prompt give their definitions;
# 4. A prompt writes a summary of the text;
# 5. A python script create a new markdown with the corrections and definitions.

######################################
# Input
######################################
ifndef BUILD_FOLDER
$(error "BUILD_FOLDER is not defined")
endif

ifndef MARKDOWN_FILE
$(error "MARKDOWN_FILE is not defined")
endif

ifndef LANGUAGE
$(error "LANGUAGE is not defined")
endif


######################################
# Variables
######################################
FILENAME=$(shell basename ${MARKDOWN_FILE} .md)
OUTPUT_FOLDER=${BUILD_FOLDER}/${FILENAME}

MAKEFILE_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
FILENAME := $(shell basename ${MARKDOWN_FILE} .md)
VENV_FOLDER := ${MAKEFILE_DIR}/.venv


######################################
# Settings
######################################
ACT := . ${VENV_FOLDER}/bin/activate
PER := llm-assistant run
MDE := correct-markdown


######################################
# Prompt executables
######################################
P_A := ${PER} correct-text --p language ${LANGUAGE} --p style same --p input-format markdown
P_B := ${PER} explain-correction --p language ${LANGUAGE}
P_C := ${PER} word-definition  --p language ${LANGUAGE}
P_D := ${PER} summarize --p language ${LANGUAGE}


######################################
# Scripts
######################################
S_A := ${MDE} word-diff
S_B := ${MDE} collect-bold-segments
S_C := ${MDE} render-enhanced-md
S_D := ${MDE} markdown-view


.PRECIOUS: enhanced.md data-to-render.json text_summary.json word-definitions.json definitions.json pin_defintions.json bold-segments.json explanation.json pin_diff-items.json diff-items.json pin_corrected.json correct.json pin_original.json no-html-view.json
.PHONY: enhanced.md data-to-render.json text_summary.json word-definitions.json definitions.json pin_defintions.json bold-segments.json explanation.json pin_diff-items.json diff-items.json pin_corrected.json correct.json pin_original.json no-html-view.json 

######################################
# Render enhanced markdown
######################################
enhanced.md: data-to-render.json | venv
	${ACT} && ${S_C} $^ > $@

data-to-render.json: pin_original.json pin_corrected.json explanation.json text_summary.json word-definitions.json
	jq -n --slurpfile F1 $< --slurpfile F2 $(word 2, $^) --slurpfile F3 $(word 3, $^) --slurpfile F4 $(word 4, $^) --slurpfile F5 $(word 5, $^) '{"MarkdownFile":"${MARKDOWN_FILE}", "Original":$$F1[0].message, "Corrected": $$F2[0].message, "CorrectionsExplanations": $$F3[0], "Summary":$$F4[0].message,"WordsDefinitions":$$F5[0]}' > $@


######################################
# Summarize
######################################
text_summary.json: pin_corrected.json | venv
	${ACT} && cat $< | ${P_D} > $@


######################################
# Find definitions of bold-faced words
######################################
.PHONY: definitions.json word-definitions.json

word-definitions.json: definitions.json bold-segments.json
	jq -n --slurpfile X $< --slurpfile Y $(word 2,$^) '[$$Y[0],$$X[0]] | transpose | .[] | {"Word":.[0],"Definition":.[1]}' | jq -s '.' > $@

definitions.json: pin_definitions.json | venv
	${ACT} && cat $< | tr \\n \\0 | xargs -0  -I[] ${P_C} --from-text '[]' | jq -s '.[] | .[0]' | jq -s '.' > $@

pin_definitions.json: bold-segments.json
	jq -cr '.[] | {"message":.}'  $< > $@

bold-segments.json:  pin_corrected.json | venv
	${ACT} && ${S_B} $^ > $@


######################################
# Explain Errors
######################################
explanation.json: pin_diff-items.json | venv
	${ACT} && cat $< | tr \\n \\0 | xargs -0 -I[] ${P_B} --from-text '[]' | jq -s '.' > $@ 

pin_diff-items.json: diff-items.json
	cat $< | jq -cr '.[] | {"message":.}' > $@

diff-items.json: pin_original.json pin_corrected.json | venv
	${ACT} && ${S_A} $^ > $@


######################################
# Generate corrected version
######################################
pin_corrected.json: correct.json
	cat $< | jq -r '{"message":.}' > $@

correct.json: pin_original.json | venv
	# The extra jq instruction is to parse eventual json string repr output into a json object
	${ACT} && cat $< | ${P_A} | jq "." > $@

pin_original.json: no-html-view.md
	jq --null-input --rawfile message $< '{"message":$$message}' > $@

no-html-view.md: | venv
	${ACT} && cat ${MARKDOWN_FILE} | ${S_D} > $@


######################################
# Pre-requisites
######################################
venv: ${VENV_FOLDER}

${VENV_FOLDER}:
	dev/create-venv/create-venv.sh

