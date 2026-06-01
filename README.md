# Map Icons QGIS Plugin

A comprehensive QGIS plugin that provides a wide range of map icons with metadata display, designed for mapping applications. The plugin automatically downloads icons and metadata from Zenodo, ensuring users always have access to the latest icon library.

## Features

- **Automatic Data Management**: Automatically downloads icons and metadata from Zenodo
- **Rich Icon Library**: Access to hundreds of professionally designed map icons
- **Primary Tag Labels**: Icons display descriptive category labels (e.g., "university", "park", "coffee")
- **Comprehensive Metadata**: View detailed information about each icon including designer, creation date, and context
- **Smart Organization**: Icons with labels displayed first, followed by unlabeled icons
- **Easy Integration**: Apply selected icons directly to QGIS point layers
- **Caching System**: Efficient local caching to minimize repeated downloads

## Icon Categories

The plugin includes icons for various mapping categories:
- **Education**: university, high-school, elementary
- **Recreation**: park, playground, gym, basketball courts
- **Transportation**: walking-path, traffic
- **Commerce**: coffee shops, shoe stores, Newbury Comics
- **Landmarks**: historical landmarks, Harvard, Empire
- **Housing**: luxury condos, Boston Housing Authority projects
- **Nature**: esplanade, concentration of tulips/dahlias
- **Events**: marathon, food festival, rally
- **And many more...**

## Installation

### Prerequisites
- QGIS 3.0 or higher
- Python 3.6 or higher
- Internet connection for initial data download

### Method 1: QGIS Plugin Manager (Recommended)
1. Open QGIS
2. Go to **Plugins** → **Manage and Install Plugins**
3. Search for "Map Icons"
4. Click **Install Plugin**

### Method 2: Manual Installation
1. Download the plugin source code
2. Extract to your QGIS plugins directory:
   - **Windows**: `C:\Users\[username]\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
3. Restart QGIS
4. Enable the plugin in **Plugins** → **Manage and Install Plugins**

### Dependencies

**Important**: QGIS uses its own Python environment. You must install dependencies manually.

The plugin requires this Python package for downloading from Zenodo:
- `requests` (≥2.25.0)

Metadata is loaded from CSV using Python's built-in `csv` module (no extra install).

#### Installing Dependencies

**Option 1: Using qpip Plugin (Recommended)**
1. Install the [qpip plugin](https://plugins.qgis.org/plugins/qpip/) from QGIS Plugin Manager
2. qpip will automatically detect and install missing dependencies for all plugins

**Option 2: Using QGIS Python Console**
1. Open QGIS
2. Go to **Plugins** → **Python Console**
3. Run:
   ```python
   import subprocess, sys
   subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
   ```

**Option 3: Using Command Line (Windows with OSGeo4W)**
1. Open **OSGeo4W Shell**
2. Run:
   ```bash
   python -m pip install requests
   ```

**Option 4: Using QGIS Python Executable**
- **Windows**: `"C:\Program Files\QGIS 3.x\bin\python3.exe" -m pip install requests`
- **macOS**: `/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install requests`
- **Linux**: `/usr/bin/python3 -m pip install requests`

**Note**: If pip is not available in your QGIS Python environment, you may need to install it first through your QGIS installation method (e.g., OSGeo4W setup).

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

### Common Issues

**Icons not displaying**
- Check internet connection for initial download
- Verify QGIS plugin directory permissions
- Clear plugin cache and restart QGIS

**Metadata not loading**
- Ensure the metadata CSV downloaded from Zenodo (check plugin cache folder)
- Verify Zenodo file accessibility
- Check QGIS Python Console for errors

**Download failures**
- Check firewall/network settings
- Verify Zenodo service status
- Try clearing cache and restarting

### Logs and Debugging
- Enable QGIS logging for detailed error information
- Check plugin cache directory for downloaded files
- Verify Python package installations

## Development

### Project Structure
```
map_icons/
├── __init__.py              # Plugin initialization
├── map_icons.py             # Main plugin class
├── map_icons_dialog.py      # Main dialog interface
├── config.py                # Configuration settings
├── data_manager.py          # Data download and caching
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── cache/                  # Local data cache (auto-created)
    ├── icons/              # Downloaded icon files
    └── metadata/           # Downloaded metadata files
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Building from Source
```bash
# Clone repository
git clone [repository-url]
cd map_icons

# Install dependencies
pip install -r requirements.txt

# Run tests (if available)
python -m pytest tests/
```

## License

This plugin is released under the **GNU General Public License v2.0** (GPL-2.0).

## Support

- **Issues**: Report bugs and feature requests via GitHub Issues
- **Documentation**: See the help files included with the plugin
- **Community**: Join QGIS user forums for general support

## Acknowledgments

- **Icon Designers**: Workshop participants who created the original icons
- **Leventhal Map and Education Center**: Hosting the icon creation workshop
- **QGIS Community**: Providing the excellent mapping platform
- **Zenodo**: Hosting the icon library and metadata

## Version History

- **v1.0.0**: Initial release with Zenodo integration
- **v0.9.0**: Beta version with primary tag labeling
- **v0.8.0**: Alpha version with basic icon display

---

**Note**: This plugin requires an internet connection for initial setup and data updates. All data is cached locally for offline use after the first download. 