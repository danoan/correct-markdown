from danoan.correct_markdown.core.markdown_view import MarkdownView 
from danoan.correct_markdown.core.model import DiffItem, TextDiffMode

from bs4 import BeautifulSoup
import difflib
import logging
import markdown
import re
import sys
from typing import Generator, List, TextIO

logger = logging.getLogger(__file__)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)


def get_plain_text_from_markdown(text: TextIO):
    html = markdown.markdown(text.read())
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()


def extract_html_tags(html):
    tag_pattern = r"</?[^>]+>"
    tag_indexes = []
    if re.search(tag_pattern, html):
        for m in re.finditer(tag_pattern, html):
            if m.group(0).find("</") != -1:
                tag_indexes.append(("closing", m.span()[0], m.span()[1]))
            else:
                tag_indexes.append(("opening", m.span()[0], m.span()[1]))
    else:
        tag_indexes.append(("markdown", 0, len(html)))

    return sorted(tag_indexes, key=lambda x: x[2])


def text_diff(
    text_a: TextIO,
    text_b: TextIO,
    mode: TextDiffMode,
    context_size: int = 10,
    update_a: bool = False,
) -> Generator[DiffItem, None, None]:
    """
    Compare two streams splited according to the given mode.

    If mode is TextDiffMode.Letter, the streams are compared letter by letter.
    If mode is TextDiffMode.Word, some characters such as whitespaces and new lines are ignored.

    The context_size gives the number of letter or words surrounding the diff that is returned
    as context.

    If update_a, then the baseline stream is updated with the found diff before the search
    for the next diff is started.
    """
    seq1, seq2, joiner = None, None, None
    if mode == TextDiffMode.Letter:
        seq1 = text_a.read()
        seq2 = text_b.read()
        joiner = ""
    elif mode == TextDiffMode.Word:
        seq1 = text_a.read().split()
        seq2 = text_b.read().split()
        joiner = " "

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


def strikethrough_errors(text: TextIO, diff_items: List[DiffItem]):
    mv = MarkdownView(text)
    start = 0
    for index, item in enumerate(diff_items, 1):
        """
        I need to guarantee that I am not replacing html markers.
        The text I receive is the raw markdown file, but the diff items
        were computed over a text-only markdown. I need to do the
        strikethrough using the text-only version but render the
        markdown one.

        This explains several flaws found during the strikethrough
        markers.
        """
        footnote_index = f"[^{index}]"

        old_value = f"{item.original_value}"
        new_value = f"~~{item.original_value}~~ {item.new_value}{footnote_index}"

        start = mv.find(old_value, start)

        mv.replace(start, old_value, new_value)
        start += len(new_value)

    return mv.get_full_content()
