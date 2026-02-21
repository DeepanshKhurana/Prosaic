# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-02-21

### Added

- **Continue writing mode**: Resume your last edited document with `c` keybinding on dashboard.
- Last file tracking stored in `settings.json`.

### Changed

- All imports moved to module level following PEP 8 conventions.
- `git.Repo` import uses `try/except ImportError` pattern for optional dependency.

## [0.1.0] - 2026-02-20

### Added

- Initial release of Prosaic writing app.
- Dashboard with pieces, books, notes, and file finder.
- Markdown editor with live outline and word counting.
- Focus mode and reader mode.
- Daily metrics tracking.
- Git-ready archive with automatic initialization.
- Git repository detection during setup wizard with remote URL inheritance.
- XDG-compliant config location (`~/.config/prosaic/`) with `XDG_CONFIG_HOME` support.
- `PROSAIC_CONFIG_DIR` environment variable for custom config path override.
- Light and dark themes.
