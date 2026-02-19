"""TextArea subclass with live spell-check underlines."""

import re

from rich.style import Style
from spellchecker import SpellChecker
from textual.binding import Binding
from textual.widgets import TextArea
from textual.widgets.text_area import TextAreaTheme

PROSAIC_LIGHT_TA = TextAreaTheme(
    name="prosaic_light",
    base_style=Style(color="#5a3d35", bgcolor="#fffffc"),
    gutter_style=Style(color="#8a6d60", bgcolor="#fffffc"),
    cursor_style=Style(color="#fffffc", bgcolor="#703327"),
    cursor_line_style=Style(bgcolor="#fffffc"),
    cursor_line_gutter_style=Style(color="#5a3d35", bgcolor="#fffffc"),
    bracket_matching_style=Style(bgcolor="#ffffed", bold=True),
    selection_style=Style(bgcolor="#ffffed"),
    syntax_styles={
        "string": Style(color="#715e12"),
        "comment": Style(color="#8a6d60", italic=True),
        "keyword": Style(color="#703327", bold=True),
        "heading": Style(color="#703327", bold=True),
    },
)

PROSAIC_DARK_TA = TextAreaTheme(
    name="prosaic_dark",
    base_style=Style(color="#e8d5c4", bgcolor="#1a1a1a"),
    gutter_style=Style(color="#8a7a6a", bgcolor="#1a1a1a"),
    cursor_style=Style(color="#1a1a1a", bgcolor="#dcae91"),
    cursor_line_style=Style(bgcolor="#1a1a1a"),
    cursor_line_gutter_style=Style(color="#e8d5c4", bgcolor="#1a1a1a"),
    bracket_matching_style=Style(bgcolor="#3a3020", bold=True),
    selection_style=Style(bgcolor="#3a3020"),
    syntax_styles={
        "string": Style(color="#c9a86c"),
        "comment": Style(color="#8a7a6a", italic=True),
        "keyword": Style(color="#dcae91", bold=True),
        "heading": Style(color="#dcae91", bold=True),
    },
)

_SKIP_LINE = re.compile(r"^(#{1,6}\s|```|---|\s*[-*+]\s|\s*\d+\.\s|>\s|!\[)")
_WORD = re.compile(r"\b([a-zA-Z']{3,})\b")
_SPELL_STYLE = Style(underline=True, color="#c24038")


class SpellCheckTextArea(TextArea):
    """TextArea with live spell-check underlines."""

    BINDINGS = [Binding("ctrl+a", "select_all", "select all", show=False)]

    def __init__(self, *args, **kwargs) -> None:
        self._spell: SpellChecker = SpellChecker()
        self._misspelled: dict[int, list[tuple[int, int]]] = {}
        requested_theme = kwargs.pop("theme", "prosaic_light")
        super().__init__(*args, theme="css", **kwargs)
        self.register_theme(PROSAIC_LIGHT_TA)
        self.register_theme(PROSAIC_DARK_TA)
        self.theme = requested_theme

    def _scan_spelling(self, text: str) -> None:
        self._misspelled.clear()
        in_frontmatter = False
        in_code_block = False

        for row, line in enumerate(text.split("\n")):
            stripped = line.strip()

            if row == 0 and stripped == "---":
                in_frontmatter = True
                continue
            if in_frontmatter:
                if stripped == "---":
                    in_frontmatter = False
                continue

            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            if not stripped or _SKIP_LINE.match(stripped):
                continue

            spans: list[tuple[int, int]] = []
            for m in _WORD.finditer(line):
                word = m.group(1).strip("'")
                if self._spell.unknown([word]):
                    spans.append((m.start(), m.end()))
            if spans:
                self._misspelled[row] = spans

    def _build_highlight_map(self) -> None:
        try:
            if self._theme is not None:
                self._theme.syntax_styles["spell.error"] = _SPELL_STYLE
        except Exception:
            pass

        self._scan_spelling(self.text)
        super()._build_highlight_map()

        for row, spans in self._misspelled.items():
            for col_s, col_e in spans:
                self._highlights[row].append((col_s, col_e, "spell.error"))
