from danoan.correct_markdown.core import api, model, utils
from danoan.correct_markdown.core.string_view import StringView

from enum import Enum
import io
import logging
import re
import sys
from typing import Any, Dict, List, Optional, TextIO, Tuple

logger = logging.getLogger(__file__)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)

###########################
# Model
###########################


class DiffOperation(Enum):
    Insert = "insert"
    Delete = "delete"
    Replace = "replace"
    Equal = "equal"


class SegmentType(Enum):
    EditableContent = "no_html"
    NoEditableContent = "html"


SegmentsDict = Dict[SegmentType, List[str]]

###########################
# Helper Functions
###########################


def build_segments(
    segments: Dict[Any, Any],
    base_string: TextIO,
    compare_string: TextIO,
    replace,
    insert,
    equal,
    delete,
):
    """
    Create StringView segments from a list of diffs between a compare string and a base string.

    Example:
        base_string:    <span>Today is a wonderful day!</span>
        compare_string: Today is a wonderful day!

        diffs:
            - Insert(<span>)
            - Equal(Today is a wonderful day!)
            - Insert(</span>

        The diff events are used to arbitrate how the string segments are created.
        In the example above, one could separate html tags from text content.
    """
    for di in api.text_diff(compare_string, base_string, model.TextDiffMode.Letter):
        operation = DiffOperation(di.operation)
        if operation == DiffOperation.Replace:
            replace(segments, di)
        elif operation == DiffOperation.Insert:
            insert(segments, di)
        elif operation == DiffOperation.Equal:
            equal(segments, di)
        elif operation == DiffOperation.Delete:
            delete(segments, di)


def build_pure_markdown_segments(original_markdown: TextIO):
    """
    Create StringView segments for a markdown document.

    The EditableContent will contain plain text and also markdown markups. That
    is.

    Example:
        original_markdown: <span>Today is a **wonderful** day!</span>

        EditableContent: Today is a **wonderful** day!
        NoEditableContent: <span></span>
    """
    pure_markdown = utils.remove_html_tags(original_markdown)
    original_markdown.seek(0)

    ss_pure_markdown = io.StringIO(pure_markdown)

    def replace(segments: SegmentsDict, di: model.DiffItem):
        tags = utils.extract_html_tags(di.new_value)
        pos = 0
        for t in tags:
            t_start, t_end = t[1:]
            segments[SegmentType.EditableContent].append(di.new_value[pos:t_start])
            segments[SegmentType.NoEditableContent].append(di.new_value[t_start:t_end])
            pos = t_end

    def insert(segments: SegmentsDict, di: model.DiffItem):
        segments[SegmentType.EditableContent].append("")
        segments[SegmentType.NoEditableContent].append(di.new_value)

    def equal(segments: SegmentsDict, di: model.DiffItem):
        segments[SegmentType.EditableContent].append(di.original_value)
        segments[SegmentType.NoEditableContent].append("")

    def delete(segments: SegmentsDict, di: model.DiffItem):
        logger.error("Non expected delete operation:", di.original_value, di.new_value)

    segments: SegmentsDict = {}
    segments[SegmentType.EditableContent] = []
    segments[SegmentType.NoEditableContent] = []
    build_segments(
        segments,
        original_markdown,
        ss_pure_markdown,
        replace,
        insert,
        equal,
        delete,
    )

    return segments


def build_plain_text_segments(original_markdown: TextIO):
    """
    Create StringView segments for a markdown document.

    The EditableContent will contain plain text and no markdown markups. That
    is.

    Example:
        original_markdown: <span>Today is a **wonderful** day!</span>

        EditableContent: Today is a wonderful day!
        NoEditableContent: <span>****</span>
    """
    plain_text = utils.get_plain_text_from_markdown(original_markdown)
    original_markdown.seek(0)

    ss_plain_text = io.StringIO(plain_text)

    def replace(segments: SegmentsDict, di: model.DiffItem):
        logger.error("Non expected replace operation:", di.original_value, di.new_value)

    def insert(segments: SegmentsDict, di: model.DiffItem):
        segments[SegmentType.EditableContent].append("")
        segments[SegmentType.NoEditableContent].append(di.new_value)

    def equal(segments: SegmentsDict, di: model.DiffItem):
        segments[SegmentType.EditableContent].append(di.original_value)
        segments[SegmentType.NoEditableContent].append("")

    def delete(segments: SegmentsDict, di: model.DiffItem):
        logger.error("Non expected delete operation:", di.original_value, di.new_value)

    segments: SegmentsDict = {}
    segments[SegmentType.EditableContent] = []
    segments[SegmentType.NoEditableContent] = []
    build_segments(
        segments,
        original_markdown,
        ss_plain_text,
        replace,
        insert,
        equal,
        delete,
    )

    return segments


class MarkdownView:
    """
    Find and replace plain-text content in a markdown string without disrupting markdown and html markups.

    This class is designed to do replace operations in the plain-text content of a markdown string.
    All markdown and html markups should remain the same and not be affected by a replace operation.

    The only exception is when the plain-text string being replaced is spread over two or more
    non-contiguous text segments. In this case, the new value is put in the first segment.
    """

    def __init__(self, original_markdown: TextIO, keep_markdown_tags: bool = False):
        if keep_markdown_tags:
            segments_pure_markdown = build_pure_markdown_segments(original_markdown)
            self.SV = StringView(segments_pure_markdown)
        else:
            segments_plain_text = build_plain_text_segments(original_markdown)

            self.SV = StringView(segments_plain_text)

        self.text_view = self.SV[SegmentType.EditableContent]

    def find(
        self,
        search_value: str,
        start: Optional[int] = None,
        end: Optional[int] = None,
        ignore_trailing_spaces: bool = True,
    ) -> Tuple[int, int]:
        """
        Find the search value in the non new line text view and return the start and end indexes.

        The start and end parameters limit the search to a substring.
        If ignore_trailing_spaces then "searched value" will match "searched    value".
        """
        if start is None:
            start = 0

        words = search_value.split()
        if len(words) == 0:
            s = self.text_view.find(re.escape(search_value), start, end)
            if s == -1:
                return s, s
            else:
                return s, s + len(search_value)

        p = ""
        if ignore_trailing_spaces:
            for w in words[:-1]:
                p += rf"{re.escape(w)}[\s\n]*"

            p += f"{re.escape(words[-1])}"
        else:
            p = " ".join(words)

        m = re.search(p, self.text_view[start:])
        if not m:
            return -1, -1

        m_s, m_e = m.span()
        return start + m_s, start + m_e

    def replace(self, t_start: int, old_value: str, new_value: str):
        """
        Replace old value by new value in text view and update segments.

        1. Find the indexes ts,te in the text view that corresponding to the old value.
        2. Find the segments ms, me in the index that correspond to ts,te.
        3. If ms==me then the old value is within the same segment and
           we can do a simple replacement.
        4. If ms!=me then the old value is spread over more than one segment.
           We put the text content within (ms,me) segments of type text in
           the segment ms (the first one) and do the replace operation there.
           Next we erase the segments (ms+1...ms_end); and merge segments of
           equal type that become contiguous after the delete operation.
        5. We need to update the index.
        """
        ti_start, ti_end = self.find(old_value, t_start)

        m_start = self.SV.get_mindex(ti_start, SegmentType.EditableContent)
        m_end = self.SV.get_mindex(ti_end - 1, SegmentType.EditableContent)

        if m_start == m_end:
            suffix = self.SV[SegmentType.EditableContent][ti_end:]
            if len(new_value) == 0:
                # In case of a delete, remove the whitespace
                self.SV[SegmentType.EditableContent] = (
                    ti_start - 1,
                    new_value + suffix,
                )
            else:
                self.SV[SegmentType.EditableContent] = (
                    ti_start,
                    new_value + suffix,
                )
        else:
            after = self.SV[SegmentType.EditableContent][ti_end:]
            self.SV[SegmentType.EditableContent] = (
                ti_start,
                new_value + after,
            )

            delete = []
            for i in range(m_start + 1, m_end + 1):
                if self.SV.index[i].view_name == SegmentType.EditableContent:
                    delete.append(i)
            self.SV.remove(*delete)

        self.text_view = self.SV[SegmentType.EditableContent]

    def get_full_content(self) -> str:
        """
        Return a string joining all pure markdown, HTML tags and plain-text segments.
        """
        return self.SV.get_content()

    def get_no_html_view(self) -> str:
        """
        Return a string joining all pure markdown and plain-text segments.
        """
        return self.SV[SegmentType.EditableContent]

    def get_html_view(self) -> str:
        """
        Return a string joining HTML tags segments.
        """
        return self.SV[SegmentType.NoEditableContent]

    def __len__(self):
        return len(self.SV[SegmentType.EditableContent])

    def __getitem__(self, key):
        return self.SV[SegmentType.EditableContent][key]
