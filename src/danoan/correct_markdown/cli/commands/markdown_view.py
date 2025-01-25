from danoan.correct_markdown.core import utils
import argparse
import logging
import sys
from typing import TextIO

logger = logging.getLogger(__file__)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)


def __markdown_view__(markdown: TextIO, **kwargs):
    """
    Print pure markdown string without html tags.
    """

    print(utils.remove_html_tags(markdown))


def extend_parser(subparser_action):
    command = "markdown-view"
    description = __markdown_view__.__doc__
    help = description.split(".")[0] if description else ""

    parser = subparser_action.add_parser(command, help=help, description=description)
    parser.add_argument(
        "markdown", nargs="?", default=sys.stdin, type=argparse.FileType("r")
    )

    parser.set_defaults(func=__markdown_view__, help=parser.print_help)
