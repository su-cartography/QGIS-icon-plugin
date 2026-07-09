## galleryofpossibilities (GAL.op): A QGIS plugin for place-based map icons

A QGIS plugin and place-based map icon library for the city of Boston initially comprised of map icons generated in community workshops. Map icons reflect experiences and power dynamics of place and include rich metadata. Icons and metadata are downloaded automatically from Zenodo on first use and cached locally for faster access afterward.

## Features

- **Automatic data management** — downloads PNG/SVG icons and CSV metadata from Zenodo
- **Local caching** — data stored under `cache/` inside the plugin folder
- **Metadata** — designer, tags, geography, description, context, and more
- **File Format** — choose betwen SVGs and PNGs when applying icons to point layers
- **Search** — filter by primary, secondary, designer, and geography tags
- **Stylize** — customize size, line color, and background color
- **Favorites** — create a personalized icon library


## Tutorial: Quick start

1. Install the plugin (see [Installation](#installation) below).
2. In QGIS, open **Plugins → Map Icons → Map Icons**.
3. On first launch, allow the plugin to download data from Zenodo (requires internet).
4. Browse or search icons, click one to view metadata in the right panel.
5. Create a point feature or elect a point layer in your map, choose PNG or SVG if available, and click **OK**.

## Installation

### Prerequisites

- QGIS 3.0 or higher
- Internet connection for the initial download

### Option 1: QGIS Plugin Manager (recommended)

1. Open QGIS
2. Go to **Plugins → Manage and Install Plugins**
3. Search for **GAL.op**
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

No additional Python packages are required. The plugin uses the Python standard
library (`urllib.request`, `csv`, `zipfile`) and QGIS's bundled PyQt.

## Usage

### Getting Started
1. **Launch the Plugin**: Go to **Plugins** → **Map Icons** → **Map Icons**
2. **Initial Setup**: On first run, the plugin will automatically download icons and metadata from Zenodo
3. **Browse Icons**: Browse through the organized grid of icons with their category labels
4. **Select an Icon**: Click on any icon to view its detailed metadata in the right panel
5. **Apply to Map**: Select a point layer in QGIS and click **OK** to apply the selected icon

### Interface Features
- **Icon Grid**: Organized display of icons with primary tag labels
- **Metadata Panel**: Detailed information about selected icons
- **Search and Filter**: Find specific icon categories quickly
- **Preview**: See how icons will look on your map

### Data Management
- **Automatic Updates**: Plugin checks for new data on startup
- **Local Caching**: Icons and metadata are cached locally for fast access
- **Manual Refresh**: Clear cache and re-download data if needed

## Data Source

All icons and metadata are sourced from the **Boston Workshop Icons** project, available on Zenodo:
- **DOI**: [10.5281/zenodo.16882205](https://doi.org/10.5281/zenodo.16882205)
- **Source**: Created as part of "Mapping Boston through Place" workshop at the Leventhal Map and Education Center
- **License**: Creative Commons Attribution 4.0 International

## Configuration

The plugin can be configured through the `config.py` file:
- **Zenodo URLs**: Links to icon and metadata files
- **Display Settings**: Icon size, grid layout, label styling
- **Cache Directories**: Local storage locations

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
- Moses Kamya and Bhumika Dashari
- Open Source Program Office (Collin Capano and Will Gearty) at Syracuse University (Sloan Funding: G-2023-20946 and G-2025-79206)
- The Maxwell School at Syrcause University (Tenth Decade Fund)
- Leventhal Map and Education Center at the Boston Public Library
- [Zenodo](https://zenodo.org/) for hosting the icon library and metadata
- The QGIS community
