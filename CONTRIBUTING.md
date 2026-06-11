# Contributing to Map Icons

Thank you for your interest in contributing! This guide explains how to get set
up, make changes, and submit them for review.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
By participating, you agree to uphold it. Report concerns to **mkelly51@syr.edu**
or via [GitHub Issues](https://github.com/su-cartography/QGIS-icon-plugin/issues).

## Ways to Contribute

- Report bugs or request features via [GitHub Issues](https://github.com/su-cartography/QGIS-icon-plugin/issues)
- Fix bugs or implement features via pull requests
- Improve documentation (README, this file, install instructions)
- Test the plugin on your QGIS version and report results

## Getting Started

### 1. Fork and clone

1. [Fork](https://github.com/su-cartography/QGIS-icon-plugin/fork) the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR-USERNAME/QGIS-icon-plugin.git
cd QGIS-icon-plugin
```

3. Add the upstream remote (if not already configured):

```bash
git remote add upstream https://github.com/su-cartography/QGIS-icon-plugin.git
git fetch upstream
```

### 2. Create a branch

Branch from `upstream/main` for each change:

```bash
git checkout -b your-branch-name upstream/main
```

Use a short, descriptive branch name, for example:

- `fix/issue-22-metadata-panel-layout`
- `docs/issue-5-install-and-contributor-guide`
- `chore/csv-metadata-drop-openpyxl`

Keep unrelated changes on separate branches and in separate pull requests.

### 3. Install for development

See [README.md — Installation](README.md#installation) for full install steps.
Summary:

1. Copy plugin folder into your QGIS plugins directory
2. Restart QGIS and enable the plugin

**Plugin directories:**

| OS | Path |
|----|------|
| Windows | `C:\Users\<username>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\` |
| macOS | `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/` |
| Linux | `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/` |

On first run, the plugin downloads icons and metadata from Zenodo into a local
`cache/` folder inside the plugin directory.

## Development Workflow

### Making changes

1. Edit code or documentation on your branch
2. Test in QGIS when your change affects plugin behavior
3. Run automated checks when possible (see below)
4. Commit with a clear message describing **why** the change was made

### Running tests

Some tests run without QGIS installed. From the repository root:

```bash
pip install -r requirements.txt
python -m compileall -q .
python test/test_init.py
python test/test_plugin_core.py
```

Full dialog and QGIS integration tests require a local QGIS installation.
CI runs the no-QGIS tests on pull requests (see `.github/workflows/ci.yml`).

### Submitting a pull request

1. Push your branch to your fork:

```bash
git push -u origin your-branch-name
```

2. Open a pull request against **`su-cartography/QGIS-icon-plugin` → `main`**
3. Fill in the PR description:
   - What changed and why
   - Link related issues (e.g. `Fixes #5`)
   - Note how you tested the change
4. Respond to review feedback and update the branch as needed

If `main` moves ahead while your PR is open:

```bash
git fetch upstream
git rebase upstream/main
git push --force-with-lease
```

## Pull Request Guidelines

- **One topic per PR** — easier to review and merge
- **Keep diffs focused** — avoid unrelated formatting or drive-by changes
- **Match existing style** — naming, imports, and patterns used in nearby code
- **Update docs** when you change install steps, dependencies, or user-facing behavior
- **Reference issues** with `Fixes #N` or `Closes #N` when applicable

## Project Layout

```
├── __init__.py              # Plugin entry point
├── map_icons.py             # Main plugin class
├── map_icons_dialog.py      # Dialog and metadata display
├── map_icons_dialog_base.ui # Qt Designer UI
├── config.py                # Zenodo URLs and display settings
├── data_manager.py          # Download and cache from Zenodo
├── requirements.txt         # Python dependencies (CI / dev)
├── test/                    # Unit tests
└── cache/                   # Local cache (created at runtime, not in git)
```

## License

Contributions are released under the same license as this project. See
[LICENSE.md](LICENSE.md).

