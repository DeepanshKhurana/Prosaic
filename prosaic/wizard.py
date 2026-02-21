"""First-run setup wizard for Prosaic."""

from pathlib import Path

import click

from prosaic.config import get_config_path, load_config

try:
    from git import Repo
except ImportError:
    Repo = None


def needs_setup() -> bool:
    """Check if first-run setup is needed."""
    config_path = get_config_path()
    if not config_path.exists():
        return True
    config = load_config()
    return not config.get("setup_complete", False)


def _prompt_git_remote() -> str:
    click.echo()
    click.echo("enter a git remote url to sync your writing (optional)")
    click.echo("(press enter to skip)")
    return click.prompt("git remote", default="", show_default=False)


def run_setup() -> dict:
    """Run the interactive setup wizard."""
    click.echo()
    click.secho("welcome to prosaic", fg="yellow", bold=True)
    click.echo("let's set things up.\n")

    default_dir = str(Path.home() / "Prosaic")
    click.echo("where should prosaic store your writing?")
    click.echo(f"(press enter for default: {default_dir})")
    archive_dir = click.prompt(
        "archive directory",
        default=default_dir,
        show_default=False,
    )
    archive_path = Path(archive_dir).expanduser().resolve()

    git_dir = archive_path / ".git"
    existing_git = git_dir.exists()
    init_git = False
    git_remote = ""

    if existing_git:
        click.echo()
        click.secho("git repository detected!", fg="cyan")
        init_git = True

        if Repo is not None:
            try:
                repo = Repo(archive_path)
                if repo.remotes:
                    git_remote = repo.remotes.origin.url
                    click.echo(f"  remote: {git_remote}")
                else:
                    click.echo("  local only (no remote configured)")
                    git_remote = _prompt_git_remote()
            except Exception:
                click.echo("  (could not read git details)")
        else:
            click.echo("  (git not available)")
    else:
        click.echo()
        init_git = click.confirm(
            "initialize git repository for version control?",
            default=True,
        )

        if init_git:
            git_remote = _prompt_git_remote()

    click.echo()
    click.secho("setup complete!", fg="green", bold=True)
    click.echo(f"  archive: {archive_path}")
    if existing_git:
        click.echo("  git: inherited existing repository")
    else:
        click.echo(f"  git: {'yes' if init_git else 'no'}")
    if git_remote:
        click.echo(f"  remote: {git_remote}")
    click.echo()

    return {
        "setup_complete": True,
        "archive_dir": str(archive_path),
        "init_git": init_git,
        "git_remote": git_remote,
        "git_inherited": existing_git,
    }


def setup_workspace(config: dict) -> None:
    """Create workspace directories based on config."""
    archive_dir = Path(config.get("archive_dir", Path.home() / "Prosaic"))

    dirs = [
        archive_dir,
        archive_dir / "pieces",
        archive_dir / "books",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    notes = archive_dir / "notes.md"
    if not notes.exists():
        notes.write_text("# Notes\n\n")

    metrics = archive_dir / "metrics.json"
    if not metrics.exists():
        metrics.write_text('{"daily": {}, "sessions": []}')

    if config.get("init_git", True) and Repo is not None:
        git_dir = archive_dir / ".git"
        try:
            if git_dir.exists():
                repo = Repo(archive_dir)
            else:
                repo = Repo.init(archive_dir)

            remote_url = config.get("git_remote", "")
            if remote_url and not repo.remotes:
                try:
                    repo.create_remote("origin", remote_url)
                except Exception:
                    pass
        except Exception:
            pass
