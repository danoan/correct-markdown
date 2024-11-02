# Given a markdown file, it does the following:
# 1. A prompt find errors in the text and generates a correct version;
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

ifndef TITLE
$(error "TITLE is not defined")
endif

######################################
# Variables
######################################

MAKEFILE_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
FILENAME=$(shell basename ${MARKDOWN_FILE} .md)
OUTPUT_FOLDER=${BUILD_FOLDER}/${FILENAME}
VENV_FOLDER=${MAKEFILE_DIR}/.venv

######################################
# Settings
######################################

PER=llm-assistant run
MDE=correct-markdown
ACT=. $(VENV_FOLDER)/bin/activate

P_A=${PER} correct-text --p language ${LANGUAGE} --p style same --p format markdown
P_B=${PER} explain-correction --p language ${LANGUAGE}
P_C=${PER} word-definition  --p language ${LANGUAGE}
P_D=${PER} summarize --p language ${LANGUAGE}

S_A=${MDE} word-diff
S_B=${MDE} collect-bold-segments
S_C=${MDE} render-enhanced-md
S_D=${MDE} markdown-view

######################################
# Targets
######################################

enhance-markdown: ${OUTPUT_FOLDER}/enhanced-md.md

${OUTPUT_FOLDER}:
	mkdir -p ${OUTPUT_FOLDER}

${VENV_FOLDER}:
	dev/create-venv/create-venv.sh

######################################
# Generate corrected version
######################################

${OUTPUT_FOLDER}/no_html_view.md: | ${OUTPUT_FOLDER}
	cat ${MARKDOWN_FILE} | ${S_D} > $@

${OUTPUT_FOLDER}/pin_original.json: ${OUTPUT_FOLDER}/no_html_view.md | ${OUTPUT_FOLDER}
	jq --null-input --rawfile message $< '{"message":$$message}' > $@

${OUTPUT_FOLDER}/correct.json: ${OUTPUT_FOLDER}/pin_original.json | ${VENV_FOLDER}
	${ACT} && cat $< | ${P_A} > $@
	# ${ACT} && cat $< | ${P_A}

${OUTPUT_FOLDER}/pin_correct.json: ${OUTPUT_FOLDER}/correct.json
	cat $< | jq '{"message":.message}' > $@

######################################
# Explain Errors
######################################

${OUTPUT_FOLDER}/diff-items.json: ${OUTPUT_FOLDER}/pin_original.json ${OUTPUT_FOLDER}/pin_correct.json
	${S_A} $^ > $@

${OUTPUT_FOLDER}/pin_diff-items.json.list: ${OUTPUT_FOLDER}/diff-items.json
	cat $< | jq -cr '.[] | {"message":.}' > $@

${OUTPUT_FOLDER}/explanation.json: ${OUTPUT_FOLDER}/pin_diff-items.json.list
	${ACT} && cat $< | xargs -d"\n" -I[] ${P_B} --from-text '[]' | jq -s '.' > $@

######################################
# Find definitions of bold-faced words
######################################

${OUTPUT_FOLDER}/bold-segments.json:  ${OUTPUT_FOLDER}/pin_correct.json
	${S_B} $^ > $@

${OUTPUT_FOLDER}/pin_definitions.json.list: ${OUTPUT_FOLDER}/bold-segments.json
	jq -cr '.[] | {"message":.}'  $< > $@

${OUTPUT_FOLDER}/definitions.json: ${OUTPUT_FOLDER}/pin_definitions.json.list
	${ACT} && cat $< | xargs -d"\n" -I[] ${P_C} --from-text '[]' | jq -s '.[] | .[0]' | jq -s '.' > $@

${OUTPUT_FOLDER}/word-definition.json: ${OUTPUT_FOLDER}/definitions.json ${OUTPUT_FOLDER}/bold-segments.json
	jq -n --slurpfile X $< --slurpfile Y $(word 2,$^) '[$$Y[0],$$X[0]] | transpose | .[] | {"Word":.[0],"Definition":.[1]}' | jq -s '.' > $@

######################################
# Summarize
######################################

${OUTPUT_FOLDER}/summarize.json: ${OUTPUT_FOLDER}/pin_correct.json
	${ACT} && cat $< | ${P_D} > $@

######################################
# Render enhanced markdown
######################################

${OUTPUT_FOLDER}/render-data.json: ${OUTPUT_FOLDER}/pin_original.json ${OUTPUT_FOLDER}/pin_correct.json ${OUTPUT_FOLDER}/explanation.json ${OUTPUT_FOLDER}/summarize.json ${OUTPUT_FOLDER}/word-definition.json
	jq -n --slurpfile F1 $< --slurpfile F2 $(word 2, $^) --slurpfile F3 $(word 3, $^) --slurpfile F4 $(word 4, $^) --slurpfile F5 $(word 5, $^) '{"MarkdownFile":"${MARKDOWN_FILE}", "Title":"${TITLE}", "Original":$$F1[0].message, "Corrected": $$F2[0].message, "CorrectionsExplanations": $$F3[0], "Summary":$$F4[0].message,"WordsDefinitions":$$F5[0]}' > $@

${OUTPUT_FOLDER}/enhanced-md.md: ${OUTPUT_FOLDER}/render-data.json
	${S_C} $^ > $@
