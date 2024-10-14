from dataclasses import dataclass
import logging
import sys
from functools import reduce
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__file__)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)


class StringView:
    r"""
    Data structure that partitionates a string in several segments that can be edited
    separately and joined altogether.

    Segments are grouped into views and represent a semantic unit in the string. An html
    document might have the markuo view containing the tag elements and the text view
    containing the plain-text content of the document.

    StringView manages a list of ViewSegmentItem (index). Each ViewSegmentItem
    describes a segment of one of the managed views.

    Below, an example of the index:
        [
            ViewSegmentItem(view_name='text', master_index=0, segment_index=0)
            ViewSegmentItem(view_name='markup', master_index=1, segment_index=0)
            ViewSegmentItem(view_name='text', master_index=2, segment_index=0)
            ViewSegmentItem(view_name='markup', master_index=3, segment_index=3)
            ViewSegmentItem(view_name='text', master_index=4, segment_index=29)
            ViewSegmentItem(view_name='markup', master_index=5, segment_index=3)
            ViewSegmentItem(view_name='text', master_index=6, segment_index=29)
        ]

    The index allows us to update both markup and text views independently. It is
    guaranteed that when "get_content" is called, both updated views will be correctly
    aligned.



    >>> segments = {
    ...  "text": ["","October journal","\n\n","October first","\n\n", "Today it rained."],
    ...  "markup": ["<h1>","</h1>","<h2>","</h2>","",""]
    ... }
    >>> SV = StringView(segments)

    >>> SV["text"]
    'October journal\n\nOctober first\n\nToday it rained.'

    >>> SV["markup"]
    '<h1></h1><h2></h2>'

    >>> SV.get_content()
    '<h1>October journal</h1>\n\n<h2>October first</h2>\n\nToday it rained.'


    >>> s = SV["text"].find("October first")
    >>> SV["text"] = s, "Monday, October first\n\nToday was sunny!"
    >>> SV["text"]
    'October journal\n\nMonday, October first\n\nToday was sunny!'


    >>> SV.get_content()
    '<h1>October journal</h1>\n\n<h2>Monday, October first</h2>\n\nToday was sunny!'
    """

    @dataclass
    class ViewSegmentItem:
        view_name: Any
        master_index: int
        segment_index: int

    def __init__(self, segments: Dict[str, List[str]]):
        self.index: List[StringView.ViewSegmentItem] = []
        self.views = {}

        previous = None
        for s in segments.values():
            if previous:
                assert len(s) == previous
            previous = len(s)

        number_views = len(segments.keys())
        total_segments = reduce(lambda x, y: x + y, [len(v) for v in segments.values()])

        # TODO: Build the temp_index in sequence instead of by segment type
        temp_index: List[Optional[StringView.ViewSegmentItem]] = [None] * total_segments
        for start_master_index, item in enumerate(segments.items()):
            name, list_segments = item
            last_seg_index = 0

            for i, content in enumerate(list_segments):
                m_index = start_master_index + i * number_views

                temp_index[m_index] = self.ViewSegmentItem(
                    name, m_index, last_seg_index
                )
                last_seg_index += len(content)

        # Populate index
        # TODO: Populate self.index directly instead of traversing temp_index.
        # This is done to have a sound typecheck.
        for el in temp_index:
            if el is not None:
                self.index.append(el)
            else:
                raise RuntimeError(
                    "Found a None value in the index. This is not expected."
                )

        # Populate views
        for key, values in segments.items():
            self.views[key] = "".join(segments[key])

    def __update_index__(
        self, m_index: int, diff_len: int, view_name: Optional[str] = None
    ):
        for i in range(m_index, len(self.index)):
            if view_name:
                if view_name == self.index[i].view_name:
                    self.index[i].segment_index += diff_len
            else:
                self.index[i].segment_index += diff_len

            self.index[i].master_index = i

    def __merge_consecutive_segments__(self):
        segments_seq_to_merge: List[List[int]] = []

        cur_sequence = []
        last_seg_type: Optional[str] = None
        for i in range(len(self.index)):
            cur_seg_type = self.index[i].view_name
            if cur_seg_type == last_seg_type:
                cur_sequence.append(i)
            else:
                segments_seq_to_merge.append([])
                cur_sequence = segments_seq_to_merge[-1]
            last_seg_type = cur_seg_type

        for g in segments_seq_to_merge:
            g.reverse()
            for d in g:
                self.index.pop(d)
        self.__update_index__(0, 0)

    def __get_segs__(self, view_name: Any):
        return filter(lambda x: x.view_name == view_name, self.index)

    def __getitem__(self, key):
        return self.views[key]

    def __setitem__(self, key, value):
        seg_index, content = value

        new_content = self.views[key][:seg_index] + content
        diff_len = len(new_content) - len(self.views[key])
        m_index = self.get_mindex(seg_index, key)

        self.views[key] = self.views[key][:seg_index] + content
        self.__update_index__(m_index + 1, diff_len, key)

    def get_mindex(self, seg_index: int, view_name: str) -> int:
        last_m = 0
        for el in self.__get_segs__(view_name):
            if el.segment_index <= seg_index:
                last_m = el.master_index
            else:
                break
        return last_m

    def remove(self, *m_indexes):
        for i in sorted(m_indexes, reverse=True):
            self.index.pop(i)
        self.__merge_consecutive_segments__()

    def get_content(self):
        s = ""

        to_zip = []
        for name in self.views.keys():
            segs = list(self.__get_segs__(name))
            segs.append(None)
            mod = []
            for s1, s2 in zip(segs[:-1], segs[1:]):
                if s2 is None:
                    s1.end = len(self[name])
                else:
                    s1.end = s2.segment_index
                mod.append(s1)
            to_zip.append(mod)

        for lv in zip(*to_zip):
            for v in lv:
                s += self[v.view_name][v.segment_index : v.end]

        return s
