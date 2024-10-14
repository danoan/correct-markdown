from danoan.correct_markdown.core import api, model

import io


def test_text_diff_word_and_update():
    text_a = "Here is the list of items\n\n - Banana\n - Apple\n - Soda."
    text_b = "Here is the list of items\n\n\n - Orange\n - Tomato\n - Soda."

    ssa = io.StringIO(text_a)
    ssb = io.StringIO(text_b)

    diff_items = list(api.text_diff(ssa, ssb, model.TextDiffMode.Word, 10, True))
    assert diff_items[0].original_value == "Banana"
    assert diff_items[0].new_value == "Orange"
    assert diff_items[0].operation == "replace"

    assert diff_items[1].original_value == "Apple"
    assert diff_items[1].new_value == "Tomato"
    assert diff_items[1].operation == "replace"
    assert diff_items[1].context == "Here is the list of items - Orange - ___ - Soda."


def test_text_diff_word_and_no_update():
    text_a = "Here is the list of items\n\n - Banana\n - Apple\n - Soda."
    text_b = "Here is the list of items\n\n\n - Orange\n - Tomato\n - Soda."

    ssa = io.StringIO(text_a)
    ssb = io.StringIO(text_b)

    diff_items = list(api.text_diff(ssa, ssb, model.TextDiffMode.Word, 10, False))
    assert diff_items[0].original_value == "Here is the list of items -"
    assert diff_items[0].new_value == diff_items[0].original_value
    assert diff_items[0].operation == "equal"

    assert diff_items[1].original_value == "Banana"
    assert diff_items[1].new_value == "Orange"
    assert diff_items[1].operation == "replace"

    assert diff_items[2].original_value == "-"
    assert diff_items[2].new_value == "-"
    assert diff_items[2].operation == "equal"

    assert diff_items[3].original_value == "Apple"
    assert diff_items[3].new_value == "Tomato"
    assert diff_items[3].operation == "replace"
    assert diff_items[3].context == "Here is the list of items - Banana - ___ - Soda."


def test_text_diff_letter_and_update():
    text_a = "Here is the list of items\n\n - Banana\n - Apple\n - Soda."
    text_b = "Here is the list of items\n\n\n - Orange\n - Tomato\n - Soda."

    ssa = io.StringIO(text_a)
    ssb = io.StringIO(text_b)

    diff_items = list(api.text_diff(ssa, ssb, model.TextDiffMode.Letter, 10, True))
    print(diff_items)
    assert diff_items[0].original_value == " - Banana"
    assert diff_items[0].new_value == ""
    assert diff_items[0].operation == "delete"

    assert diff_items[1].original_value == "Appl"
    assert diff_items[1].new_value == "Orang"
    assert diff_items[1].operation == "replace"

    assert diff_items[2].original_value == ""
    assert diff_items[2].new_value == "Tomato\n - "
    assert diff_items[2].operation == "insert"


def test_get_plain_text_from_markdown():
    ss = io.StringIO(
        '# The ultimate guide\n\nThe **ultimate guide** will lead you to the <span style="color:blue">path</span> you want to achieve.'
    )

    plain_text = api.get_plain_text_from_markdown(ss)
    assert (
        plain_text
        == "The ultimate guide\nThe ultimate guide will lead you to the path you want to achieve."
    )


def test_extract_html_tags():
    s = '# The ultimate guide\n\nThe **ultimate guide** will lead you to the <span style="color:blue">path</span> you want to achieve.'
    tags = list(api.extract_html_tags(s))

    assert tags[0] == ("opening", 66, 91)
    assert tags[1] == ("closing", 95, 102)
