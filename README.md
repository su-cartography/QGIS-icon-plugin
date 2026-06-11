# Map Icons QGIS Plugin

A QGIS plugin that provides map icons with rich metadata. Icons and metadata are
downloaded automatically from Zenodo on first use and cached locally for faster
access afterward.

## Features

- **Automatic data management** — downloads PNG/SVG icons and CSV metadata from Zenodo
- **Searchable icon grid** — filter by primary and secondary tags
- **Metadata panel** — designer, tags, geography, description, context, and more
- **PNG and SVG** — choose format when applying icons to point layers
- **Local caching** — data stored under `cache/` inside the plugin folder

## Tutorial: Quick start

1. Install the plugin (see [Installation](#installation) below).
2. In QGIS, open **Plugins → Map Icons → Map Icons**.
3. On first launch, allow the plugin to download data from Zenodo (requires internet).
4. Browse or search icons, click one to view metadata in the right panel.
5. Select a point layer in your map, choose PNG or SVG if available, and click **OK**.

## Installation

### Prerequisites

- QGIS 3.0 or higher
- Internet connection for the initial download

### Option 1: QGIS Plugin Manager (recommended)

1. Open QGIS
2. Go to **Plugins → Manage and Install Plugins**
3. Search for **Map Icons**
4. Click **Install Plugin**

### Option 2: Manual installation

1. Clone or download this repository
2. Copy the plugin folder into your QGIS plugins directory:

| OS | Path |
|----|------|
| Windows | `C:\Users\<username>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\` |
| macOS | `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/` |
| Linux | `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/` |

3. Restart QGIS
4. Enable the plugin under **Plugins → Manage and Install Plugins**

## Usage

- **Search** — use the search box to filter by primary or secondary tags
- **Metadata** — click an icon to show details in the side panel
- **Format** — switch between PNG and SVG when both are available
- **Apply** — select a point layer, pick an icon, click **OK**

## Data source

Icons and metadata come from the Boston Workshop Icons collection on Zenodo:

- **DOI**: [10.5281/zenodo.20126394](https://doi.org/10.5281/zenodo.20126394)
- **Record**: [zenodo.org/records/20126394](https://zenodo.org/records/20126394)
- **License**: Creative Commons Attribution 4.0 International (dataset)


## Troubleshooting

**Icons or metadata not loading**

- Check your internet connection on first run
- Check **View → Panels → Log Messages** for plugin errors
- Delete the `cache/` folder inside the plugin directory and restart QGIS to re-download

**Plugin not visible after manual install**

- Confirm the folder is directly under `plugins/` (not nested incorrectly)
- Restart QGIS and enable the plugin in the Plugin Manager

## Contributing

Contributions are welcome! Please read:

- [CONTRIBUTING.md](CONTRIBUTING.md) — development setup, tests, and pull request workflow
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — community standards

Report bugs or request features via
[GitHub Issues](https://github.com/su-cartography/QGIS-icon-plugin/issues).

## Development

```bash
git clone https://github.com/su-cartography/QGIS-icon-plugin.git
cd QGIS-icon-plugin
pip install -r requirements.txt
python test/test_init.py
python test/test_plugin_core.py
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow.

## Contact

- **Issues**: [github.com/su-cartography/QGIS-icon-plugin/issues](https://github.com/su-cartography/QGIS-icon-plugin/issues)
- **Maintainer**: Moses Kamya — mkamya@syr.edu

## License

This plugin is licensed under the GNU General Public License. See [LICENSE.md](LICENSE.md).

## Acknowledgments

- Workshop participants who created the original icons
- Leventhal Map and Education Center — *Mapping Boston through Place* workshop
- [Zenodo](https://zenodo.org/) for hosting the icon library and metadata
- The QGIS community
