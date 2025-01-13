from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


@dataclass
class DiffItem:
    context: str
    original_value: str
    new_value: str
    operation: str


@dataclass
class Metadata:
    markdown_file: str
    original: str
    corrected: str
    corrections_explanations: List[str]
    summary: str
    words_definitions: Dict[str, str]


class TextDiffMode(Enum):
    Letter = "letter"
    Word = "word"
