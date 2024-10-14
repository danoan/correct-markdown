import json
import logging
from pathlib import Path
import re
import sys
from typing import TextIO

logger = logging.getLogger(__file__)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)


def collect_bold_segments(text: TextIO):
    r_bold_expression = r"\*\*([^\*]*)\*\*"
    for seg in re.findall(r_bold_expression, text.read()):
        yield seg


def __collect_bold_segments__(text_a: Path, **kwargs):
    """
    Collect all segments in between double asteristics.
    """
    if not text_a.exists():
        logger.error(f"File {text_a} does not exist")
        exit(1)

    with open(text_a) as f:
        json.dump(list(collect_bold_segments(f)), sys.stdout, ensure_ascii=False)


def extend_parser(subparser_action):
    command = "collect-bold-segments"
    description = __collect_bold_segments__.__doc__
    help = description.split(".")[0] if description else ""

    parser = subparser_action.add_parser(command, help=help, description=description)
    parser.add_argument("text_a", type=Path)

    parser.set_defaults(func=__collect_bold_segments__, help=parser.print_help)
