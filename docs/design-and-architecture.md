# Design and Architecture

This document lists the design and architectural decisions taken
during the development of Correct Markdown. It follows
the [Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions.html) format.

## StringView

**Date: (2024-10-01)**


### Context

The project goal is to correct pieces of text in a markdown document. This task cannot be done
with a straightforward find and replace because the markdown document contains information other
than plain-text, namely markdown tags and, eventually, html tags.

We need a data-structure to isolate markup information from plain-text information.

### Decision

Create StringView data-structure. This data-structure maintains an index and a view object
where the subsets of a string partition can be edited independently from each other.

To initialize a StringView we have to pass a partition of string. A partition is a collection of
disjoint sets which the union gives the original string. A partition is described by a dictionary
where the key represents the set name (view name) and the value represents the list of strings
the set is made of.

During initialization we build the index and view objects. The index is a list of `ViewSegmentItem`

```python
@dataclass
class ViewSegmentItem:
    view_name: Any
    master_index: int
    segment_index: int
```

After initialization, one can update a view without affecting the others.

```python
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
```
Notice that to replace a view segment we can bracket reference the view and then assign it
to an integer and a string. The integer represents the position in the view from where to
start the reassignment and the string is the new content.

### Status

Implemented.

### Consequences

Refactor strikethrough-items to start using StringView. It is likely the case that a helper
data-structure will be needed to address special requirements for the markdown correction
feature.

## MarkdownView

**Date: (2024-10-05)**


### Context

- Do diff analysis in a word-basis: trailing spaces and new lines are ignored.
- Do diff analysis in a letter-basis: trailing spaces and new lines are taken into account.
- In MarkdownView use `get_plain_text_from_html`: That way we start to considering markdown markup
  as part of the text_view. The idea is to avoid the behaviour during replace where if the replaced
  value is spread over two or more segments, the new value is stored in the first one.
  A common case is when we have a correction to be done in a word that is in between **. Whenever
  the correction spread over outside the closing **, we change the substring enclosed by **.
  TODO: Rename get_plain_text_from_html to remove_html_tags


### Decision

### Status

### Consequences
