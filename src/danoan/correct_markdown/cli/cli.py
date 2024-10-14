from danoan.correct_markdown.cli.commands import (
    collect_bold,
    markdown_view,
    render_enhanced_md,
    word_diff,
)

import argparse
import logging
from pathlib import Path
import sys

logger = logging.getLogger(__file__)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)

SCRIPT_FOLDER = Path(__file__).parent


def main():
    parser = argparse.ArgumentParser("correct-markdown")
    subparser = parser.add_subparsers()

    commands = [
        collect_bold,
        markdown_view,
        render_enhanced_md,
        word_diff,
    ]
    for cmd in commands:
        cmd.extend_parser(subparser)

    args = parser.parse_args()
    if "func" in args:
        args.func(**vars(args))
    elif "help" in args:
        args.help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
