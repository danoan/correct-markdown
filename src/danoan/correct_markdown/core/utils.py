from danoan.correct_markdown.core.markdown_view import MarkdownView
from danoan.correct_markdown.core.model import DiffItem

import re
from typing import List, Tuple, TextIO


def extract_html_tags(html: str) -> List[Tuple[str, int, int]]:
    """
    Parses a html string and extracts all its markup tags.

    Each returned item is a triplet (type,start,end)

    type:
        closing: closing html tag
        opening: opening html tag
        no_html: text content
    """
    tag_pattern = r"</?[^>]+>"
    tag_indexes = []
    if re.search(tag_pattern, html):
        for m in re.finditer(tag_pattern, html):
            if m.group(0).find("</") != -1:
                tag_indexes.append(("closing", m.span()[0], m.span()[1]))
            else:
                tag_indexes.append(("opening", m.span()[0], m.span()[1]))
    else:
        tag_indexes.append(("no_html", 0, len(html)))

    return sorted(tag_indexes, key=lambda x: x[2])


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

    if item.operation == "insert":
        start, end = s, s
    elif item.operation == "delete":
        end = start
    elif item.operation == "replace":
        start, end = mv.find(item.original_value, s)

    mv.replace(start, old_value, item.new_value)
    if start + len(item.new_value) > end:
        end = start + len(item.new_value)

    return start, end


def render_diff_view(
    markdown_stream: TextIO,
    diff_items: List[DiffItem],
    insert=None,
    delete=None,
    replace=None,
):
    mv = MarkdownView(markdown_stream)
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
