from danoan.correct_markdown.core import utils


def test_extract_html_tags():
    s = '# The ultimate guide\n\nThe **ultimate guide** will lead you to the <span style="color:blue">path</span> you want to achieve.'
    tags = list(utils.extract_html_tags(s))

    assert tags[0] == ("opening", 66, 91)
    assert tags[1] == ("closing", 95, 102)
