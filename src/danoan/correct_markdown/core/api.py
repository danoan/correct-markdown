from danoan.correct_markdown.core.markdown_view import MarkdownView
from danoan.correct_markdown.core.model import DiffItem, TextDiffMode

import difflib
import logging
import sys
from typing import Generator, List, TextIO, Tuple

logger = logging.getLogger(__file__)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)


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
        sm = difflib.SequenceMatcher(None, seq1, seq2, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if update_a and tag == "equal":
                continue

            context_before = joiner.join(seq1[max(0, i1 - context_size) : i1])
            context_after = joiner.join(seq1[i2 : i2 + context_size])
            action_segment = joiner.join(seq1[i1:i2])
            context = f"{context_before} ___ {context_after}"

            yield DiffItem(context, action_segment, joiner.join(seq2[j1:j2]), tag)

            if update_a:
                seq1 = seq2[max(j2 - 10, 0) : j2] + seq1[i2:]
                seq2 = seq2[max(j2 - 10, 0) :]
                break
        else:
            break


def strikethrough_errors(markdown_stream: TextIO, diff_items: List[DiffItem]) -> str:
    def insert(item: DiffItem, index: int):
        footnote_index = f"[^{index}]"
        return f"{item.new_value}{footnote_index} "

    def delete(item: DiffItem, index: int):
        footnote_index = f"[^{index}]"
        return f"~~{item.original_value}~~ {item.new_value}{footnote_index}"

    def replace(item: DiffItem, index: int):
        footnote_index = f"[^{index}]"
        return f"~~{item.original_value}~~ {item.new_value}{footnote_index}"

    return render_diff_view(markdown_stream, diff_items, insert, delete, replace)


def apply_corrections(markdown_stream: TextIO, diff_items: List[DiffItem]) -> str:
    def insert(item: DiffItem, index: int):
        return item.new_value

    def delete(item: DiffItem, index: int):
        return item.new_value

    def replace(item: DiffItem, index: int):
        return item.new_value

    return render_diff_view(markdown_stream, diff_items, insert, delete, replace)


def apply_diff(mv: MarkdownView, item: DiffItem, start: int = 0) -> Tuple[int, int]:
    """
    Apply correction in markdown view contained in the diff item.

    We use the item.original_value and its after context to find the correct
    position in the markdown view where the diff operation will take place. The
    after context is important to avoid false positives, which can be quite common
    when the original_value is short such as `the`,` one` and so on.
    """
    old_value = f"{item.original_value}"

    after = item.context.split("___")[1]
    search_value = f"{item.original_value} {after}"
    s, e = mv.find(search_value, start)
    if s == -1:
        raise ValueError({"message": "Value not found", "search_value": search_value})

    start = s
    end = e

    mv.replace(start, old_value, item.new_value)
    end = start + len(item.new_value)

    return start, end


def render_diff_view(
    markdown_stream: TextIO,
    diff_items: List[DiffItem],
    insert=None,
    delete=None,
    replace=None,
) -> str:
    mv = MarkdownView(markdown_stream, True)
    start = 0
    for index, item in enumerate(diff_items, 1):
        if item.operation == "insert" and insert:
            item.new_value = insert(item, index)
        elif item.operation == "delete":
            item.new_value = delete(item, index)
        elif item.operation == "replace":
            item.new_value = replace(item, index)

        s, e = apply_diff(mv, item, start)
        start = e

    return mv.get_full_content()
