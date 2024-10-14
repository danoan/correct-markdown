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

        assert len(mv) == 309
        assert len(mv.get_text_view()) == 309
        assert len(mv.get_markup_view()) == 263
        assert len(mv.get_full_content()) == len(original)
        assert len(mv) + len(mv.get_markup_view()) == len(mv.get_full_content())
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
    with open(INPUT_FOLDER / "test_e" / "text_a.md") as fa, open(
        INPUT_FOLDER / "test_e" / "text_b.md"
    ) as fb:
        original = fa.read()
        expected = fb.read()

        sa = io.StringIO(original)
        sb = io.StringIO(expected)

        tv1 = MarkdownView(sa)
        tv2 = MarkdownView(sb)

        pt1 = io.StringIO(tv1.get_text_view())
        pt2 = io.StringIO(tv2.get_text_view())

        diff_items = list(api.text_diff(pt1, pt2, model.TextDiffMode.Word, 10, True))

        pt1.seek(0)
        start = 0
        for i, di in enumerate(diff_items):
            if di.operation == "insert":
                before, after = di.context.split("___")
                start = tv1.find(before, start - len(before)) + len(before)
                new_value = di.new_value + " "
            else:
                start = tv1.find(di.original_value, start)
                new_value = di.new_value

            tv1.replace(start, di.original_value, new_value)
            start += len(new_value)

        pt2.seek(0)
        assert tv1.get_text_view() == tv2.get_text_view()
        assert tv1.get_full_content() == tv2.get_full_content()
