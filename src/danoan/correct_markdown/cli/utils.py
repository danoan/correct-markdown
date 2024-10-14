from danoan.correct_markdown.core import api, model

import io
import json
from pathlib import Path
from typing import List, TextIO


def get_diff_items(text_a: TextIO, text_b: TextIO) -> List[model.DiffItem]:
    ss_a = io.StringIO()
    # ss_a.write(api.get_plain_text_from_markdown(text_a))
    ss_a.write(api.remove_html_tags(text_a))

    ss_b = io.StringIO()
    # ss_b.write(api.get_plain_text_from_markdown(text_b))
    ss_b.write(api.remove_html_tags(text_b))

    ss_a.seek(0)
    ss_b.seek(0)

    return list(api.text_diff(ss_a, ss_b, model.TextDiffMode.Word, 10, True))


def get_diff_items_from_path(text_a: Path, text_b: Path) -> List[model.DiffItem]:
    message_a, message_b = None, None
    with open(text_a) as fa, open(text_b) as fb:
        message_a = json.load(fa)["message"]
        message_b = json.load(fb)["message"]

    ss_a = io.StringIO()
    ss_a.write(message_a)
    ss_b = io.StringIO()
    ss_b.write(message_b)

    ss_a.seek(0)
    ss_b.seek(0)

    return get_diff_items(ss_a, ss_b)
