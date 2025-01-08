from danoan.correct_markdown.core import api, model
from danoan.correct_markdown.core.markdown_view import MarkdownView

import io
from pathlib import Path

SCRIPT_FOLDER = Path(__file__).parent
INPUT_FOLDER = SCRIPT_FOLDER / "input"


def test_a():
    with open(INPUT_FOLDER / "test_a" / "text_a.md") as fa:
        original = fa.read()
        ss = io.StringIO(original)
        mv = MarkdownView(ss)

        assert len(mv) == 317
        assert len(mv.get_no_html_view()) == 317
        assert len(mv.get_html_view()) == 255
        assert len(mv.get_full_content()) == len(original)
        assert len(mv) + len(mv.get_html_view()) == len(mv.get_full_content())
        assert mv.get_full_content() == original


def test_b():
    with open(INPUT_FOLDER / "test_b" / "text_a.md") as fa, open(
        INPUT_FOLDER / "test_b" / "text_b.md"
    ) as fb:
        original = fa.read()
        expected = fb.read()

        ss = io.StringIO(original)
        mv = MarkdownView(ss)

        mv.replace(0, "Claude:", "Daniel:")
        assert mv.get_full_content() == expected


def test_c():
    with open(INPUT_FOLDER / "test_c" / "text_a.md") as fa, open(
        INPUT_FOLDER / "test_c" / "text_b.md"
    ) as fb:
        original = fa.read()
        expected = fb.read()

        ss = io.StringIO(original)
        mv = MarkdownView(ss)
        mv.replace(0, "Claude:  Que mangerons-nous", "Daniel: On mange quoi")
        assert mv.get_full_content() == expected


def test_d():
    with open(INPUT_FOLDER / "test_d" / "text_a.md") as fa, open(
        INPUT_FOLDER / "test_d" / "text_b.md"
    ) as fb:
        original = fa.read()
        expected = fb.read()

        ss = io.StringIO(original)
        mv = MarkdownView(ss)
        mv.replace(0, "tronche", "tête")
        assert mv.get_full_content() == expected


def test_e():
    with open(INPUT_FOLDER / "test_e" / "text_a.md") as fa, open(
        INPUT_FOLDER / "test_e" / "text_b.md"
    ) as fb:
        original = fa.read()
        expected = fb.read()

        ss = io.StringIO(original)
        mv = MarkdownView(ss)
        mv.replace(0, "tronche", "tête")
        assert mv.get_full_content() == expected


def test_f():
    with open(INPUT_FOLDER / "test_f" / "text_a.md") as fa, open(
        INPUT_FOLDER / "test_f" / "text_b.md"
    ) as fb:
        original = fa.read()
        expected = fb.read()

        sa = io.StringIO(original)
        sb = io.StringIO(expected)

        tv1 = MarkdownView(sa)
        tv2 = MarkdownView(sb)

        pt1 = io.StringIO(tv1.get_no_html_view())
        pt2 = io.StringIO(tv2.get_no_html_view())

        diff_items = list(api.text_diff(pt1, pt2, model.TextDiffMode.Word, 10, True))

        start = 0
        for di in diff_items:
            if di.operation == "insert":
                di.new_value += " "
            s, e = api.apply_diff(tv1, di, start)
            start = e

        assert tv1.get_no_html_view() == tv2.get_no_html_view()
        assert tv1.get_full_content() == tv2.get_full_content()
