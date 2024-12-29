from danoan.correct_markdown.core import api, model
from danoan.correct_markdown.core.string_view import StringView

from enum import Enum
import io
import logging
import re
import sys
from typing import Dict, List, Optional, TextIO, Tuple

logger = logging.getLogger(__file__)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)


class MarkdownView:
    """
    Find and replace plain-text content in a markdown string without disrupting markdown and html markups.

    This class is designed to do replace operations in the plain-text content of a markdown string.
    All markdown and html markups should remain the same and not be affected by a replace operation.

    The only exception is when the plain-text string being replaced is spread over two or more
    non-contiguous text segments. In this case, the new value is put in the first segment.
    """

    class SegmentType(Enum):
        NoHtml = "no_html"
        Html = "html"

    class DiffOperation(Enum):
        Insert = "insert"
        Delete = "delete"
        Replace = "replace"
        Equal = "equal"

    def __init__(self, original_markdown: TextIO):
        pure_markdown = api.remove_html_tags(original_markdown)
        original_markdown.seek(0)

        ss_text = io.StringIO(pure_markdown)
        segments: Dict[MarkdownView.SegmentType, List[str]] = {}
        segments[MarkdownView.SegmentType.NoHtml] = []
        segments[MarkdownView.SegmentType.Html] = []
        for di in api.text_diff(ss_text, original_markdown, model.TextDiffMode.Letter):
            operation = MarkdownView.DiffOperation(di.operation)
            if operation == MarkdownView.DiffOperation.Replace:
                tags = api.extract_html_tags(di.new_value)
                pos = 0
                for t in tags:
                    t_start, t_end = t[1:]
                    segments[MarkdownView.SegmentType.NoHtml].append(
                        di.new_value[pos:t_start]
                    )
                    segments[MarkdownView.SegmentType.Html].append(
                        di.new_value[t_start:t_end]
                    )
                    pos = t_end
            elif operation == MarkdownView.DiffOperation.Insert:
                segments[MarkdownView.SegmentType.NoHtml].append("")
                segments[MarkdownView.SegmentType.Html].append(di.new_value)
            elif operation == MarkdownView.DiffOperation.Equal:
                segments[MarkdownView.SegmentType.NoHtml].append(di.original_value)
                segments[MarkdownView.SegmentType.Html].append("")
            elif operation == MarkdownView.DiffOperation.Delete:
                logger.error(
                    "Non expected delete operation:", di.original_value, di.new_value
                )

        self.SV = StringView(segments)
        self.text_view = self.SV[MarkdownView.SegmentType.NoHtml]

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

        m_start = self.SV.get_mindex(ti_start, MarkdownView.SegmentType.NoHtml)
        m_end = self.SV.get_mindex(ti_end - 1, MarkdownView.SegmentType.NoHtml)

        if m_start == m_end:
            suffix = self.SV[MarkdownView.SegmentType.NoHtml][ti_end:]
            if len(new_value) == 0:
                # In case of a delete, remove the whitespace
                self.SV[MarkdownView.SegmentType.NoHtml] = (
                    ti_start - 1,
                    new_value + suffix,
                )
            else:
                self.SV[MarkdownView.SegmentType.NoHtml] = ti_start, new_value + suffix
        else:
            after = self.SV[MarkdownView.SegmentType.NoHtml][ti_end:]
            self.SV[MarkdownView.SegmentType.NoHtml] = ti_start, new_value + after

            delete = []
            for i in range(m_start + 1, m_end + 1):
                if self.SV.index[i].view_name == MarkdownView.SegmentType.NoHtml:
                    delete.append(i)
            self.SV.remove(*delete)

        self.text_view = self.SV[MarkdownView.SegmentType.NoHtml]

    def get_full_content(self) -> str:
        """
        Return a string joining all pure markdown, HTML tags and plain-text segments.
        """
        return self.SV.get_content()

    def get_no_html_view(self) -> str:
        """
        Return a string joining all pure markdown and plain-text segments.
        """
        return self.SV[MarkdownView.SegmentType.NoHtml]

    def get_html_view(self) -> str:
        """
        Return a string joining HTML tags segments.
        """
        return self.SV[MarkdownView.SegmentType.Html]

    def __len__(self):
        return len(self.SV[MarkdownView.SegmentType.NoHtml])

    def __getitem__(self, key):
        return self.SV[MarkdownView.SegmentType.NoHtml][key]
