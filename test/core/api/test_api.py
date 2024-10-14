from danoan.correct_markdown.core import api, model

import io
from pathlib import Path

SCRIPT_FOLDER = Path(__file__).parent
INPUT_FOLDER = SCRIPT_FOLDER / "input"


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


def test_strikethrough_errors_a():
    original = INPUT_FOLDER / "strikethrough" / "test_a" / "original.md"
    corrected = INPUT_FOLDER / "strikethrough" / "test_a" / "corrected.md"
    expected = INPUT_FOLDER / "strikethrough" / "test_a" / "expected.md"

    with open(original) as fa, open(corrected) as fb, open(expected) as fc:
        pa = api.get_plain_text_from_html(fa)
        pb = api.get_plain_text_from_html(fb)

        fa.seek(0)
        fb.seek(0)

        diff_items = list(
            api.text_diff(
                io.StringIO(pa), io.StringIO(pb), model.TextDiffMode.Word, 10, True
            )
        )

        response = api.strikethrough_errors(fa, diff_items)
        assert response == fc.read()


def test_strikethrough_errors_b():
    _diff_items = [
        {
            "context": "# Le ___ passionné pour le Cambodge Claude: Que mangerons-nous cet après-midi? Boris:",
            "original_value": "con",
            "new_value": "",
            "operation": "delete",
        },
        {
            "context": "# Le passionné ___ Claude: Que mangerons-nous cet après-midi? Boris: Je voudrais bien aller",
            "original_value": "pour le Cambodge",
            "new_value": "de la cuisine cambodgienne",
            "operation": "replace",
        },
        {
            "context": 'après-midi? Boris: Je voudrais bien aller chez "Les saveurs du ___ un restaurant cambodgien? Boris: Oui, exactement! Arnaud: Ça tombe bien!',
            "original_value": 'Kep" Arnaud: Est-il',
            "new_value": 'Kep". Arnaud: Est-ce',
            "operation": "replace",
        },
        {
            "context": 'Kep". Arnaud: Est-ce un restaurant cambodgien? Boris: Oui, exactement! Arnaud: ___ Je suis fasciné pour la Cambodge et sa culture. On',
            "original_value": "Ça tombe bien!",
            "new_value": "Parfait!",
            "operation": "replace",
        },
        {
            "context": "restaurant cambodgien? Boris: Oui, exactement! Arnaud: Parfait! Je suis fasciné ___ Cambodge et sa culture. On se donne rendez-vous sur place",
            "original_value": "pour la",
            "new_value": "par le",
            "operation": "replace",
        },
        {
            "context": "suis fasciné par le Cambodge et sa culture. On se ___ à 13h? Claude: Er... Ok, c'est bon.",
            "original_value": "donne rendez-vous sur place",
            "new_value": "retrouve là-bas",
            "operation": "replace",
        },
    ]

    diff_items = [model.DiffItem(**x) for x in _diff_items]

    with open(INPUT_FOLDER / "strikethrough" / "test_b" / "text_a.md") as fa, open(
        INPUT_FOLDER / "strikethrough" / "test_b" / "text_b.md"
    ) as fb:
        response = api.strikethrough_errors(fa, diff_items)
        assert response == fb.read()


def test_strikethrough_errors_c():
    _diff_items = [
        {
            "context": "pendant le protectorat. Jusqu'à ce que les Khmers rouges prennent ___ contrôle. Boris: Je suis content que les plats sont arrivées.",
            "original_value": "",
            "new_value": "le",
            "operation": "insert",
        },
        {
            "context": "prennent le contrôle. Boris: Je suis content que les plats ___ J'ai hâte pour goûter les saveurs du Kep. Claude: Le",
            "original_value": "sont arrivées.",
            "new_value": "soient arrivés.",
            "operation": "replace",
        },
        {
            "context": "Je suis content que les plats soient arrivés. J'ai hâte ___ goûter les saveurs du Kep. Claude: Le mien est délicieux!",
            "original_value": "pour",
            "new_value": "de",
            "operation": "replace",
        },
    ]
    diff_items = [model.DiffItem(**x) for x in _diff_items]

    with open(INPUT_FOLDER / "strikethrough" / "test_c" / "text_a.md") as fa, open(
        INPUT_FOLDER / "strikethrough" / "test_c" / "text_b.md"
    ) as fb:
        response = api.strikethrough_errors(fa, diff_items)
        assert response == fb.read()


def test_get_no_html_view():
    original = INPUT_FOLDER / "get_markdown_only" / "original.md"
    expected = INPUT_FOLDER / "get_markdown_only" / "expected.md"
    with open(original) as fa, open(expected) as fb:
        md_only = api.get_plain_text_from_html(fa)
        assert md_only == fb.read()
