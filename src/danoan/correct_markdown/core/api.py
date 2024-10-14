from danoan.correct_markdown.core.markdown_view import MarkdownView
from danoan.correct_markdown.core import utils
from danoan.correct_markdown.core.model import DiffItem, TextDiffMode

from bs4 import BeautifulSoup
import difflib
import logging
import markdown  # type: ignore
import sys
from typing import Generator, List, Optional, TextIO

logger = logging.getLogger(__file__)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)


def get_plain_text_from_markdown(markdown_stream: TextIO) -> str:
    """
    Removes all markdown markup from a string.
    """
    html = markdown.markdown(markdown_stream.read())
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()


def remove_html_tags(string_stream: TextIO) -> str:
    """
    Removes all html tags from a string.
    """
    content = string_stream.read()

    last = 0
    no_html = ""
    tags = utils.extract_html_tags(content)
    for tag in tags:
        name, i, j = tag
        if name == "no_html":
            no_html += content[i:j]
        else:
            no_html += content[last:i]
        last = j

    no_html += content[last:]

    return no_html


def text_diff(
    ss_a: TextIO,
    ss_b: TextIO,
    mode: TextDiffMode,
    context_size: int = 10,
    update_a: bool = False,
) -> Generator[DiffItem, None, None]:
    """
    Compare two string streams and return the differences.

    If mode is TextDiffMode.Letter, the streams are compared letter by letter.
    If mode is TextDiffMode.Word, some characters such as whitespaces and new lines are ignored.

    The context_size gives the number of letter or words surrounding the diff that is returned
    as context.

    If update_a, then the baseline stream is updated with the found diff before the search
    for the next diff is started.
    """
    seq1: List[str] = []
    seq2: List[str] = []
    joiner: str = ""
    if mode == TextDiffMode.Letter:
        seq1 = list(ss_a.read())
        seq2 = list(ss_b.read())
        joiner = ""
    elif mode == TextDiffMode.Word:
        seq1 = ss_a.read().split()
        seq2 = ss_b.read().split()
        joiner = " "
    else:
        raise RuntimeError(f"Unexpected mode: {mode}")

    while True:
        sm = difflib.SequenceMatcher(None, seq1, seq2)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if update_a and tag == "equal":
                continue

            context_before = joiner.join(seq1[max(0, i1 - context_size) : i1])
            context_after = joiner.join(seq1[i2 : i2 + context_size])
            action_segment = joiner.join(seq1[i1:i2])
            context = f"{context_before} ___ {context_after}"

            yield DiffItem(context, action_segment, joiner.join(seq2[j1:j2]), tag)

            if update_a:
                seq1 = seq2[:j2] + seq1[i2:]
                break
        else:
            break


def strikethrough_errors(markdown_stream: TextIO, diff_items: List[DiffItem]):
    def insert(item: DiffItem, index: int):
        footnote_index = f"[^{index}]"
        return f"{item.new_value}{footnote_index} "

    def delete(item: DiffItem, index: int):
        footnote_index = f"[^{index}]"
        return f"~~{item.original_value}~~ {item.new_value}{footnote_index}"

    def replace(item: DiffItem, index: int):
        footnote_index = f"[^{index}]"
        return f"~~{item.original_value}~~ {item.new_value}{footnote_index}"

    return utils.render_diff_view(markdown_stream, diff_items, insert, delete, replace)


def apply_corrections(markdown_stream: TextIO, diff_items: List[DiffItem]):
    def insert(item: DiffItem, index: int):
        return item.new_value

    def delete(item: DiffItem, index: int):
        return item.new_value

    def replace(item: DiffItem, index: int):
        return item.new_value

    return utils.render_diff_view(markdown_stream, diff_items, insert, delete, replace)
