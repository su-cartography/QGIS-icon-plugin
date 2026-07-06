# -*- coding: utf-8 -*-
"""
Configuration file for Map Icons QGIS Plugin
This file contains configuration settings for the plugin, including Zenodo URLs
for downloading icons and metadata files.
"""

# Zenodo concept DOI (always resolves to the latest published version)
# https://doi.org/10.5281/zenodo.16882204
ZENODO_CONCEPT_DOI = "10.5281/zenodo.16882204"
ZENODO_CONCEPT_RECID = 16882204
ZENODO_API_LATEST_URL = (
    f"https://zenodo.org/api/records/{ZENODO_CONCEPT_RECID}"
)

# Backward-compatible alias used in docs and citations
ZENODO_DOI = ZENODO_CONCEPT_DOI

# Expected asset filenames on Zenodo (v5 naming convention)
ZENODO_PNG_ZIP_NAME = "map-icon-png.zip"
ZENODO_SVG_ZIP_NAME = "map-icon-svg.zip"
ZENODO_METADATA_CSV_NAME = "map-icon-metadata.csv"

# Folder names inside downloaded zips
PNG_FOLDER = "map-icon-png"
SVG_FOLDER = "map-icon-svg"

# Column headers in map-icon-metadata.csv (Zenodo v5+)
METADATA_CSV_HEADERS = (
    "unique-ID",
    "designer",
    "metadata-source",
    "uploader",
    "primary-tags",
    "secondary-tags",
    "when-created",
    "when-uploaded",
    "where-created",
    "icon-geography",
    "icon-description",
    "icon-context",
    "creation-context",
    "notes",
)

# Folder names inside downloaded zips
PNG_FOLDER = "map-icon-png"
SVG_FOLDER = "map-icon-svg"

# Column headers in map-icon-metadata.csv (Zenodo v5+)
METADATA_CSV_HEADERS = (
    "unique-ID",
    "designer",
    "metadata-source",
    "uploader",
    "primary-tags",
    "secondary-tags",
    "when-created",
    "when-uploaded",
    "where-created",
    "icon-geography",
    "icon-description",
    "icon-context",
    "creation-context",
    "notes",
)
# Local cache directories
CACHE_DIR = "cache"
ICONS_CACHE_DIR = "cache/icons"
METADATA_CACHE_DIR = "cache/metadata"
ZENODO_RECORD_ID_FILE = "cache/zenodo_record_id.txt"

# Plugin settings
MAX_ICONS_PER_ROW = 5
ICON_SIZE = 80  # Increased for better visibility
BUTTON_SIZE = 100  # Increased for better clickability
LABEL_MAX_WIDTH = 140  # Wider to show full primary tags (e.g. "public-basketball-courts")
LABEL_MIN_HEIGHT = 36  # Taller for multi-line labels

# Enhanced label styling with modern design - larger font for better visibility
LABEL_STYLE = """
QLabel {
    font-size: 11px; 
    font-weight: 600;
    color: #2c3e50; 
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
        stop:0 #ffffff, stop:1 #f8f9fa);
    border: 1px solid #dee2e6; 
    border-radius: 6px;
    padding: 6px 8px;
    min-height: 36px;
}
"""

# Icon button styling - modern card design
ICON_BUTTON_STYLE = """
QPushButton {
    background-color: #ffffff;
    border: 2px solid #e9ecef;
    border-radius: 12px;
    padding: 8px;
}

QPushButton:hover {
    background-color: #f8f9fa;
    border: 2px solid #3498db;
    transform: scale(1.05);
}

QPushButton:checked {
    background-color: #e3f2fd;
    border: 3px solid #2196f3;
    border-radius: 12px;
}

QPushButton:pressed {
    background-color: #bbdefb;
    border: 3px solid #1976d2;
}
"""

# Container widget styling for card effect
CONTAINER_STYLE = """
QWidget {
    background-color: transparent;
    border-radius: 8px;
    padding: 4px;
}
"""