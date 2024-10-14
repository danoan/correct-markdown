from danoan.correct_markdown.core import api
from danoan.correct_markdown.cli import utils

import io
import logging
from pathlib import Path
import sys

logger = logging.getLogger(__file__)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)


def __corrected_view__(original_markdown: Path, plain_text_correction: Path, **kwargs):
    """
    Render plain text correction using the original markdown as template.
    """
    if not original_markdown.exists():
        print(f"Could find file {original_markdown}")
        exit(1)
    if not plain_text_correction.exists():
        print(f"Could find file {plain_text_correction}")
        exit(1)

    with open(original_markdown) as fa, open(plain_text_correction) as fb:
        ss_a = io.StringIO(fa.read())

        no_html = api.remove_html_tags(ss_a)

        ss_b = io.StringIO(fb.read())
        diff_items = utils.get_diff_items(io.StringIO(no_html), ss_b)

        ss_a.seek(0)
        r = api.apply_corrections(ss_a, diff_items)
        print(r)


def extend_parser(subparser_action):
    command = "corrected-view"
    description = __corrected_view__.__doc__
    help = description.split(".")[0] if description else ""

    parser = subparser_action.add_parser(command, help=help, description=description)
    parser.add_argument(
        "original_markdown", type=Path, help="Path to original markdown file"
    )
    parser.add_argument(
        "plain_text_correction",
        type=Path,
        help="Path to file containing the plain text correction",
    )

    parser.set_defaults(func=__corrected_view__, help=parser.print_help)
