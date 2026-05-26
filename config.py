# -*- coding: utf-8 -*-
"""
Configuration file for Map Icons QGIS Plugin

This file contains configuration settings for the plugin, including Zenodo URLs
for downloading icons and metadata files.
"""

# Zenodo DOI and URLs (v4)
# https://zenodo.org/records/20126394
ZENODO_DOI = "10.5281/zenodo.20126394"
ZENODO_BASE_URL = "https://zenodo.org/record/20126394/files"

# File URLs on Zenodo (filenames must match the record exactly)
ICONS_ZIP_URL = f"{ZENODO_BASE_URL}/sample-icon-set-PNG.zip"
SVG_ZIP_URL = f"{ZENODO_BASE_URL}/sample-icon-set-SVG.zip"
# Metadata is CSV on v4; plugin also supports .xlsx if you point METADATA_FILE_URL to one
METADATA_FILE_URL = f"{ZENODO_BASE_URL}/sample-icon-set-metadata.csv"
# Backward compatibility for imports/tests that still reference METADATA_EXCEL_URL
METADATA_EXCEL_URL = METADATA_FILE_URL

# Local cache directories
CACHE_DIR = "cache"
ICONS_CACHE_DIR = "cache/icons"
METADATA_CACHE_DIR = "cache/metadata"

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
