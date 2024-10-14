from danoan.correct_markdown.cli.commands.render_enhanced_md import render_enhanced_md


def test_render_enhanced_md():
    render_data = {
        "title": "The great Gatsby",
        "text": "From the other side of the bay we could see this greenish light coming from Gatsby mansion.",
        "summary": "Gatsby was a old sport",
        "words_definitions": [
            {"Word": "greenish", "Definition": "something that has tones of green"},
            {
                "Word": "mansion",
                "Definition": "a big and comfortable building where one or more people live",
            },
        ],
        "corrections_explanations": ["This is an example of a correction."],
    }
    enhanced_md = render_enhanced_md(render_data)
    assert (
        enhanced_md
        == """\
# The great Gatsby

From the other side of the bay we could see this greenish light coming from Gatsby mansion.

## Summary

Gatsby was a old sport

## Definitions

1. **greenish**: something that has tones of green

2. **mansion**: a big and comfortable building where one or more people live



## Corrections

[^1]: This is an example of a correction.

"""
    )
