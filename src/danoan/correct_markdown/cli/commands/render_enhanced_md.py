from danoan.correct_markdown.core import api, model
from danoan.correct_markdown.cli import utils

from dataclasses import asdict
import io
import jinja2
import json
import logging
from pathlib import Path
import sys
from typing import Any, Dict

logger = logging.getLogger(__file__)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)

env = jinja2.Environment(
    loader=jinja2.PackageLoader("danoan.correct_markdown.cli"),
    autoescape=jinja2.select_autoescape(),
)


def render_enhanced_md(render_data: Dict[str, Any]) -> str:
    template = env.get_template("enhanced_md.md.tpl")
    return template.render(**render_data)


def __render_enhanced_md__(metadata: Path, **kwargs):
    """
    Add strikethrough marks to identify modifications made among two files.
    """
    if not metadata.exists():
        logger.error(f"File {metadata} does not exist")
        exit(1)

    metadata_obj = None
    with open(metadata) as f:
        _m = json.load(f)
        m = {}
        m["markdown_file"] = _m["MarkdownFile"]
        m["title"] = _m["Title"]
        m["original"] = _m["Original"]
        m["corrected"] = _m["Corrected"]
        m["corrections_explanations"] = _m["CorrectionsExplanations"]
        m["summary"] = _m["Summary"]
        m["words_definitions"] = _m["WordsDefinitions"]
        metadata_obj = model.Metadata(**m)

    ss_a = io.StringIO()
    ss_a.write(metadata_obj.original)
    ss_a.seek(0)

    ss_b = io.StringIO()
    ss_b.write(metadata_obj.corrected)
    ss_b.seek(0)

    diff_items = utils.get_diff_items(ss_a, ss_b)
    if len(diff_items) != len(metadata_obj.corrections_explanations):
        logger.error(
            f"Length of list of corrections  does not match the length of the list of explanations. {len(diff_items)} != {len(metadata_obj.corrections_explanations)}"
        )
        exit(1)

    with open(metadata_obj.markdown_file) as f:
        render_data = asdict(metadata_obj).copy()
        render_data["text"] = api.strikethrough_errors(f, diff_items)
        print(render_enhanced_md(render_data))


def extend_parser(subparser_action):
    command = "render-enhanced-md"
    description = __render_enhanced_md__.__doc__
    help = description.split(".")[0] if description else ""

    parser = subparser_action.add_parser(command, help=help, description=description)
    parser.add_argument("metadata", type=Path)

    parser.set_defaults(func=__render_enhanced_md__, help=parser.print_help)
