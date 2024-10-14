from danoan.correct_markdown.core import api, model
from danoan.correct_markdown.core.string_view import StringView

from enum import Enum
import io
import logging
import sys
from typing import Optional, TextIO

logger = logging.getLogger(__file__)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)


class MarkdownView:
    """
        find: Find in text view
        replace: Replace in text view

    Assumptions:
        - Markdown stream is written in a markdown version that is supported
          by markdown library. The markdown library transforms the markdown into
          html which its first parsed by beautifulsoup to extract the plain-text
          segments.


    Find and replace operations are done in the text view.

    """

    class SegmentType(Enum):
        Text = "text"
        Markup = "markup"

    class DiffOperation(Enum):
        Insert = "insert"
        Delete = "delete"
        Replace = "replace"
        Equal = "equal"

    def __init__(self, original_markdown: TextIO):
        plain_text = api.get_plain_text_from_markdown(original_markdown)
        original_markdown.seek(0)

        ss_text = io.StringIO(plain_text)
        segments = {}
        segments[MarkdownView.SegmentType.Text] = []
        segments[MarkdownView.SegmentType.Markup] = []
        for di in api.text_diff(ss_text, original_markdown, model.TextDiffMode.Letter):
            operation = MarkdownView.DiffOperation(di.operation)
            if operation == MarkdownView.DiffOperation.Replace:
                tags = api.extract_html_tags(di.new_value)
                pos = 0
                for t in tags:
                    t_start, t_end = t[1:]
                    segments[MarkdownView.SegmentType.Text].append(
                        di.new_value[pos:t_start]
                    )
                    segments[MarkdownView.SegmentType.Markup].append(
                        di.new_value[t_start:t_end]
                    )
                    pos = t_end
            elif operation == MarkdownView.DiffOperation.Insert:
                segments[MarkdownView.SegmentType.Text].append("")
                segments[MarkdownView.SegmentType.Markup].append(di.new_value)
            elif operation == MarkdownView.DiffOperation.Equal:
                segments[MarkdownView.SegmentType.Text].append(di.original_value)
                segments[MarkdownView.SegmentType.Markup].append("")
            elif operation == MarkdownView.DiffOperation.Delete:
                print("Non expected delete operation:", di.original_value, di.new_value)

        self.A = StringView(segments)
        self.text_view_nw = self.A[MarkdownView.SegmentType.Text].replace("\n", " ")

    def find(
        self, search_value: str, start: Optional[int] = None, end: Optional[int] = None
    ) -> int:
        return self.text_view_nw.find(search_value, start, end)

    def replace(self, t_start: int, old_value: str, new_value: str):
        """
        Replace old value by new value in text view and update segments.

        1. Find the indexes ts,te in the text view that matched the old value.
        2. Find the segments ms, me in the index that correspond to ts,te.
        3. If ms==me then the old value is within the same segment and
           we can do a simple replacement.
        4. If ms!=me then the old value is spread over more than one segment.
           We put the text content within (ms,me) segments of type text in
           the segment ms and do the replace operation there. Next we erase
           the segments (ms+1...ms_end); merge segments of same type that
           become contiguous after the delete operation.
        5. We need to update the index.

        TODO: A better algorithm would be the following:
        Assume we want to replace "aaa bbb" by "ddd" in the content below:
            [markup][aaa][markup][bbb ccc][markup]
        the idea is to reorganize the segments as:
            [markup][ddd][markup][ccc][markup]
        Current algorithm does the following:
            [markup][ddd ccc][merge<markup,markup>]
        """
        ti_start = self.text_view_nw.find(old_value, t_start)

        ti_end = ti_start + len(old_value)

        m_start = self.A.get_mindex(ti_start, MarkdownView.SegmentType.Text)
        m_end = self.A.get_mindex(ti_end - 1, MarkdownView.SegmentType.Text)

        if m_start == m_end:
            suffix = self.A[MarkdownView.SegmentType.Text][ti_end:]
            if len(new_value) == 0:
                # In case of a delete, remove the whitespace
                self.A[MarkdownView.SegmentType.Text] = ti_start - 1, new_value + suffix
            else:
                self.A[MarkdownView.SegmentType.Text] = ti_start, new_value + suffix
        else:
            after = self.A[MarkdownView.SegmentType.Text][ti_start + len(old_value) :]
            self.A[MarkdownView.SegmentType.Text] = ti_start, new_value + after

            delete = []
            for i in range(m_start + 1, m_end + 1):
                if self.A.index[i].view_name == MarkdownView.SegmentType.Text:
                    delete.append(i)

            self.A.remove(*delete)

        self.text_view_nw = self.A[MarkdownView.SegmentType.Text].replace("\n", " ")

    def get_full_content(self) -> str:
        return self.A.get_content()

    def get_text_view(self) -> str:
        return self.A[MarkdownView.SegmentType.Text]

    def get_markup_view(self) -> str:
        return self.A[MarkdownView.SegmentType.Markup]

    def __len__(self):
        return len(self.A[MarkdownView.SegmentType.Text])

    def __getitem__(self, key):
        return self.A[MarkdownView.SegmentType.Text][key]
