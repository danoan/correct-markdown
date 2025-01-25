from danoan.correct_markdown.core import api, model
from danoan.correct_markdown.core.markdown_view import MarkdownView

from bs4 import BeautifulSoup
import io
from pathlib import Path

SCRIPT_FOLDER = Path(__file__).parent
INPUT_FOLDER = SCRIPT_FOLDER / "input"


def are_html_documents_equivalent(doc1: str, doc2: str):
    soup1 = BeautifulSoup(doc1, "html.parser")
    soup2 = BeautifulSoup(doc2, "html.parser")

    normalized_soup1 = soup1.prettify()
    normalized_soup2 = soup2.prettify()

    return normalized_soup1 == normalized_soup2


######################################################
# Start of Plain-Text MarkdownView tests
######################################################


def test_pt_a():
    with open(INPUT_FOLDER / "test_a" / "text_a.md") as fa:
        original = fa.read()
        ss = io.StringIO(original)
        mv = MarkdownView(ss, False)

        assert len(mv) == 309
        assert len(mv.get_no_html_view()) == 309
        assert len(mv.get_html_view()) == 263
        assert len(mv.get_full_content()) == len(original)
        assert len(mv) + len(mv.get_html_view()) == len(mv.get_full_content())
        assert mv.get_full_content() == original


def test_pt_b():
    with open(INPUT_FOLDER / "test_b" / "text_a.md") as fa, open(
        INPUT_FOLDER / "test_b" / "text_b.md"
    ) as fb:
        original = fa.read()
        expected = fb.read()

        ss = io.StringIO(original)
        mv = MarkdownView(ss, False)

        mv.replace(0, "Claude:", "Daniel:")
        assert mv.get_full_content() == expected


def test_pt_c():
    with open(INPUT_FOLDER / "test_c" / "text_a.md") as fa, open(
        INPUT_FOLDER / "test_c" / "text_b.md"
    ) as fb:
        original = fa.read()
        expected = fb.read()

        ss = io.StringIO(original)
        mv = MarkdownView(ss, False)
        mv.replace(0, "Claude:  Que mangerons-nous", "Daniel: On mange quoi")

        assert are_html_documents_equivalent(mv.get_full_content(), expected)


def test_pt_d():
    with open(INPUT_FOLDER / "test_d" / "text_a.md") as fa, open(
        INPUT_FOLDER / "test_d" / "text_b.md"
    ) as fb:
        original = fa.read()
        expected = fb.read()

        ss = io.StringIO(original)
        mv = MarkdownView(ss, False)
        mv.replace(0, "tronche", "tête")
        assert mv.get_full_content() == expected


def test_pt_e():
    with open(INPUT_FOLDER / "test_e" / "text_a.md") as fa, open(
        INPUT_FOLDER / "test_e" / "text_b.md"
    ) as fb:
        original = fa.read()
        expected = fb.read()

        ss = io.StringIO(original)
        mv = MarkdownView(ss, False)
        mv.replace(0, "tronche", "tête")
        assert mv.get_full_content() == expected


def test_pt_f():
    with open(INPUT_FOLDER / "test_f" / "text_a.md") as fa, open(
        INPUT_FOLDER / "test_f" / "text_b.md"
    ) as fb:
        original = fa.read()
        expected = fb.read()

        sa = io.StringIO(original)
        sb = io.StringIO(expected)

        tv1 = MarkdownView(sa, False)
        tv2 = MarkdownView(sb, False)

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


######################################################
# Start of Pure-Markdown MarkdownView tests
######################################################


def test_pm_a():
    with open(INPUT_FOLDER / "test_a" / "text_a.md") as fa:
        original = fa.read()
        ss = io.StringIO(original)
        mv = MarkdownView(ss, True)

        assert len(mv) == 317
        assert len(mv.get_no_html_view()) == 317
        assert len(mv.get_html_view()) == 255
        assert len(mv.get_full_content()) == len(original)
        assert len(mv) + len(mv.get_html_view()) == len(mv.get_full_content())
        assert mv.get_full_content() == original


def test_pm_b():
    with open(INPUT_FOLDER / "test_b" / "text_a.md") as fa, open(
        INPUT_FOLDER / "test_b" / "text_b.md"
    ) as fb:
        original = fa.read()
        expected = fb.read()

        ss = io.StringIO(original)
        mv = MarkdownView(ss, True)

        mv.replace(0, "Claude:", "Daniel:")
        assert mv.get_full_content() == expected


def test_pm_c():
    with open(INPUT_FOLDER / "test_c" / "text_a.md") as fa, open(
        INPUT_FOLDER / "test_c" / "text_b.md"
    ) as fb:
        original = fa.read()
        expected = fb.read()

        ss = io.StringIO(original)
        mv = MarkdownView(ss, True)
        mv.replace(0, "Claude:  Que mangerons-nous", "Daniel: On mange quoi")

        assert are_html_documents_equivalent(mv.get_full_content(), expected)


def test_pm_d():
    with open(INPUT_FOLDER / "test_d" / "text_a.md") as fa, open(
        INPUT_FOLDER / "test_d" / "text_b.md"
    ) as fb:
        original = fa.read()
        expected = fb.read()

        ss = io.StringIO(original)
        mv = MarkdownView(ss, True)
        mv.replace(0, "tronche", "tête")
        assert mv.get_full_content() == expected


def test_pm_e():
    with open(INPUT_FOLDER / "test_e" / "text_a.md") as fa, open(
        INPUT_FOLDER / "test_e" / "text_b.md"
    ) as fb:
        original = fa.read()
        expected = fb.read()

        ss = io.StringIO(original)
        mv = MarkdownView(ss, True)
        mv.replace(0, "tronche", "tête")
        assert mv.get_full_content() == expected


def test_pm_f():
    with open(INPUT_FOLDER / "test_f" / "text_a.md") as fa, open(
        INPUT_FOLDER / "test_f" / "text_b.md"
    ) as fb:
        original = fa.read()
        expected = fb.read()

        sa = io.StringIO(original)
        sb = io.StringIO(expected)

        tv1 = MarkdownView(sa, True)
        tv2 = MarkdownView(sb, True)

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
