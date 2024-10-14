from danoan.correct_markdown.cli import utils

from dataclasses import asdict
import json
import logging
from pathlib import Path
import sys

logger = logging.getLogger(__file__)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)


def __word_diff__(text_a: Path, text_b: Path, **kwargs):
    """
    Compare two files and return a list of diff items.
    """
    if not text_a.exists():
        logger.error(f"File {text_a} does not exist")
        exit(1)
    if not text_b.exists():
        logger.error(f"File {text_b} does not exist")
        exit(1)

    diff_items = utils.get_diff_items_from_path(text_a, text_b)
    json.dump(
        [asdict(el) for el in diff_items], sys.stdout, indent=2, ensure_ascii=False
    )


def extend_parser(subparser_action):
    command = "word-diff"
    description = __word_diff__.__doc__
    help = description.split(".")[0] if description else ""

    parser = subparser_action.add_parser(command, help=help, description=description)
    parser.add_argument("text_a", type=Path)
    parser.add_argument("text_b", type=Path)

    parser.set_defaults(func=__word_diff__, help=parser.print_help)
