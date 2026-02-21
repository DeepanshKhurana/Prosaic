"""Prosaic modals and dialogs."""

from datetime import datetime
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label, ListItem, ListView, Static

from prosaic.config import get_books_dir, get_pieces_dir, get_workspace_dir

HELP_TEXT = """
shortcuts

dashboard
  s         start writing
  p         write a piece
  b         work on a book
  n         add a note
  r         read notes
  f         find files
  ?         help
  q         quit

editor
  ctrl+e    toggle file tree
  ctrl+o    toggle outline
  ctrl+s    save
  ctrl+q    go home
  f5        focus mode
  f6        reader mode

editing
  ctrl+z    undo
  ctrl+y    redo
  ctrl+x    cut
  ctrl+c    copy
  ctrl+v    paste
  ctrl+a    select all

git status
  *         modified
  +         staged
  ?         untracked

press escape or q to close
"""


class NewPieceModal(ModalScreen[Path | None]):
    """Modal for creating a new piece."""

    BINDINGS = [Binding("escape", "cancel", "cancel")]

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Static("write a piece", id="dialog-title")
            yield Static("enter a title (or leave blank for timestamp):")
            yield Input(placeholder="my-new-piece", id="title-input")

    def on_mount(self) -> None:
        self.query_one("#title-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._create_piece()

    def _create_piece(self) -> None:
        title = self.query_one("#title-input", Input).value.strip()

        if title:
            slug = title.lower().replace(" ", "-")
            slug = "".join(c for c in slug if c.isalnum() or c == "-")
            filename = f"{slug}.md"
        else:
            filename = datetime.now().strftime("%Y%m%d%H%M%S") + ".md"

        pieces_dir = get_pieces_dir()
        pieces_dir.mkdir(parents=True, exist_ok=True)
        file_path = pieces_dir / filename

        date_str = datetime.now().strftime("%Y-%m-%d")
        slug_str = filename[:-3]
        frontmatter = f'''---
title: "{title}"
date: {date_str}
slug: {slug_str}
---

'''
        file_path.write_text(frontmatter)
        self.dismiss(file_path)

    def action_cancel(self) -> None:
        self.dismiss(None)


class StartWritingModal(ModalScreen[Path | None]):
    """Modal for starting a writing session."""

    BINDINGS = [Binding("escape", "cancel", "cancel")]

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Static("start writing", id="dialog-title")
            yield Static("enter a filename (or leave blank for timestamp):")
            yield Input(placeholder="my-document", id="title-input")

    def on_mount(self) -> None:
        self.query_one("#title-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._create_file()

    def _create_file(self) -> None:
        title = self.query_one("#title-input", Input).value.strip()

        if title:
            slug = title.lower().replace(" ", "-")
            slug = "".join(c for c in slug if c.isalnum() or c == "-")
            filename = f"{slug}.md"
        else:
            filename = datetime.now().strftime("%Y%m%d%H%M%S") + ".md"

        workspace_dir = get_workspace_dir()
        workspace_dir.mkdir(parents=True, exist_ok=True)
        file_path = workspace_dir / filename

        file_path.write_text("")
        self.dismiss(file_path)

    def action_cancel(self) -> None:
        self.dismiss(None)


class NewBookModal(ModalScreen[Path | None]):
    """Modal for creating a new book."""

    BINDINGS = [Binding("escape", "cancel", "cancel")]

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Static("work on a book", id="dialog-title")
            yield Static("enter a title (or leave blank for timestamp):")
            yield Input(placeholder="my-new-book", id="title-input")

    def on_mount(self) -> None:
        self.query_one("#title-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._create_book()

    def _create_book(self) -> None:
        title = self.query_one("#title-input", Input).value.strip()

        if title:
            slug = title.lower().replace(" ", "-")
            slug = "".join(c for c in slug if c.isalnum() or c == "-")
            filename = f"{slug}.md"
        else:
            filename = datetime.now().strftime("%Y%m%d%H%M%S") + ".md"

        books_dir = get_books_dir()
        books_dir.mkdir(parents=True, exist_ok=True)
        file_path = books_dir / filename

        content = f"# {title}\n\n" if title else ""
        file_path.write_text(content)
        self.dismiss(file_path)

    def action_cancel(self) -> None:
        self.dismiss(None)


class _FileItem(ListItem):
    """List item carrying a Path reference."""

    def __init__(self, path: Path, workspace: Path) -> None:
        filename = path.stem
        
        # Check if it's the notes file
        if path.name == "notes.md":
            file_type = "n"
        else:
            try:
                rel_path = path.relative_to(workspace)
                parts = rel_path.parts
                if len(parts) > 1:
                    folder = parts[0]
                    if folder == "pieces":
                        file_type = "p"
                    elif folder == "books":
                        file_type = "b"
                    else:
                        file_type = "d"
                else:
                    file_type = "d"
            except ValueError:
                file_type = ""
        
        if file_type:
            display = f"{filename} • {file_type}"
        else:
            display = filename
        super().__init__(Label(display))
        self.path = path


class FileFindModal(ModalScreen[Path | None]):
    """Modal for finding files."""

    BINDINGS = [Binding("escape", "cancel", "cancel")]

    def compose(self) -> ComposeResult:
        with Vertical(id="find-dialog"):
            yield Static("find files", id="dialog-title")
            yield Input(placeholder="type to filter...", id="find-input")
            yield ListView(id="find-list")
            yield Static("(b)ook • (d)raft • (n)ote • (p)iece", id="find-legend")

    def on_mount(self) -> None:
        self.query_one("#find-input", Input).focus()
        self._refresh_list("")

    def on_input_changed(self, event: Input.Changed) -> None:
        self._refresh_list(event.value.strip())

    def _refresh_list(self, query: str) -> None:
        workspace_dir = get_workspace_dir()
        find_list = self.query_one("#find-list", ListView)
        find_list.clear()

        if not workspace_dir.exists():
            return

        files = sorted(
            workspace_dir.rglob("*.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if query:
            files = [f for f in files if query.lower() in f.stem.lower()]

        for f in files[:20]:
            find_list.append(_FileItem(f, workspace_dir))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if isinstance(event.item, _FileItem):
            self.dismiss(event.item.path)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        find_list = self.query_one("#find-list", ListView)
        idx = find_list.index
        items = list(find_list.query(_FileItem))
        if idx is not None and 0 <= idx < len(items):
            self.dismiss(items[idx].path)
        elif items:
            self.dismiss(items[0].path)
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)


class HelpScreen(ModalScreen):
    """Help screen showing keybindings."""

    BINDINGS = [
        Binding("escape", "close", "close"),
        Binding("q", "close", "close"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="help-dialog"):
            yield Static(HELP_TEXT.strip())

    def action_close(self) -> None:
        self.dismiss()


__all__ = ["FileFindModal", "HelpScreen", "NewBookModal", "NewPieceModal", "StartWritingModal"]
