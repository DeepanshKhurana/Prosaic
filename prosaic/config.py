"""Configuration management for Prosaic."""

import json
import os
from pathlib import Path

try:
    from git import Repo
except ImportError:
    Repo = None


def get_config_dir() -> Path:
    """Get the config directory."""
    if env_dir := os.environ.get("PROSAIC_CONFIG_DIR"):
        return Path(env_dir).expanduser().resolve()
    if xdg_config := os.environ.get("XDG_CONFIG_HOME"):
        return Path(xdg_config) / "prosaic"
    return Path.home() / ".config" / "prosaic"


def get_config_path() -> Path:
    """Get the config file path."""
    return get_config_dir() / "settings.json"


def load_config() -> dict:
    """Load configuration from settings.json."""
    config_path = get_config_path()
    if config_path.exists():
        return json.loads(config_path.read_text())
    return {}


def save_config(config: dict) -> None:
    """Save configuration to settings.json."""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2))


def get_workspace_dir() -> Path:
    """Get the archive directory from config or default."""
    config = load_config()
    archive_dir = config.get("archive_dir")
    if archive_dir:
        return Path(archive_dir)
    return Path.home() / "Prosaic"


def get_pieces_dir() -> Path:
    """Get the pieces directory."""
    return get_workspace_dir() / "pieces"


def get_books_dir() -> Path:
    """Get the books directory."""
    return get_workspace_dir() / "books"


def get_notes_path() -> Path:
    """Get the notes.md path."""
    return get_workspace_dir() / "notes.md"


def get_last_file() -> Path | None:
    """Get the last edited file path."""
    config = load_config()
    last_file = config.get("last_file")
    if last_file:
        path = Path(last_file)
        if path.exists() and path != get_notes_path():
            return path
    return None


def set_last_file(path: Path) -> None:
    """Set the last edited file path."""
    if path == get_notes_path():
        return
    config = load_config()
    config["last_file"] = str(path)
    save_config(config)


def ensure_workspace() -> None:
    """Ensure the workspace structure exists."""
    dirs = [
        get_workspace_dir(),
        get_pieces_dir(),
        get_books_dir(),
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    notes = get_notes_path()
    if not notes.exists():
        notes.write_text("# Notes\n\n")

    config = load_config()
    if config.get("init_git", True) and Repo is not None:
        workspace = get_workspace_dir()
        if not (workspace / ".git").exists():
            try:
                repo = Repo.init(workspace)
                remote_url = config.get("git_remote", "")
                if remote_url:
                    try:
                        repo.create_remote("origin", remote_url)
                    except Exception:
                        pass
            except Exception:
                pass
