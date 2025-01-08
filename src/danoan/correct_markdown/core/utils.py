from bs4 import BeautifulSoup
import markdown  # type: ignore
import re
from typing import List, Tuple, TextIO


def get_plain_text_from_markdown(markdown_stream: TextIO) -> str:
    """
    Removes all markdown markup from a string.
    """
    html = markdown.markdown(markdown_stream.read())
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()


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


def remove_html_tags(string_stream: TextIO) -> str:
    """
    Removes all html tags from a string.
    """
    content = string_stream.read()

    last = 0
    no_html = ""
    tags = extract_html_tags(content)
    for tag in tags:
        name, i, j = tag
        if name == "no_html":
            no_html += content[i:j]
        else:
            no_html += content[last:i]
        last = j

    no_html += content[last:]

    return no_html
