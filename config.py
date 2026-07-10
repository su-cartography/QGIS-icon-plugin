# -*- coding: utf-8 -*-
"""
Configuration file for Map Icons QGIS Plugin
This file contains configuration settings for the plugin, including Zenodo URLs
for downloading icons and metadata files.
"""

# Zenodo DOI and URLs (v5)
# https://zenodo.org/records/20397958
ZENODO_DOI = "10.5281/zenodo.20397958"
ZENODO_BASE_URL = "https://zenodo.org/records/20397958/files"

# File URLs on Zenodo (filenames must match the record exactly)
ICONS_ZIP_URL = f"{ZENODO_BASE_URL}/map-icon-png.zip"
SVG_ZIP_URL = f"{ZENODO_BASE_URL}/map-icon-svg.zip"
METADATA_FILE_URL = f"{ZENODO_BASE_URL}/map-icon-metadata.csv"

# Backward compatibility for imports/tests that still reference METADATA_EXCEL_URL
METADATA_EXCEL_URL = METADATA_FILE_URL

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

# Plugin settings
MAX_ICONS_PER_ROW = 5
ICON_SIZE = 80  # Increased for better visibility
BUTTON_SIZE = 100  # Increased for better clickability
LABEL_MAX_WIDTH = 140  # Wider to show full primary tags (e.g. "public-basketball-courts")
LABEL_MIN_HEIGHT = 36  # Taller for multi-line labels

# Metadata panel preview 
METADATA_PREVIEW_SIZE = 72
METADATA_PREVIEW_HEIGHT = 88
PLUGIN_ICON_FILENAME = "icon.png"

# UI theme 
DIALOG_STYLE = """
QDialog {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #f3eeff, stop:0.4 #fff0f8, stop:1 #f5ffe8);
}
"""

HEADER_STYLE = """
QLabel#dialogHeaderLabel {
    font-size: 22px;
    font-weight: 700;
    color: #3A0CA3;
    padding: 0;
    background: transparent;
}
"""

SEARCH_STYLE = """
QLineEdit {
    background-color: #ffffff;
    border: 2px solid #B5179E;
    border-radius: 14px;
    padding: 10px 16px;
    font-size: 13px;
    font-weight: 500;
    color: #3A0CA3;
    selection-background-color: #F72585;
    selection-color: #ffffff;
}
QLineEdit:focus {
    border: 2px solid #7209B7;
    background-color: #fffbfe;
}
"""

SCROLL_AREA_STYLE = """
QScrollArea {
    background: transparent;
    border: none;
}
QScrollArea > QWidget > QWidget {
    background: transparent;
}
QScrollBar:vertical {
    background: #ede9fe;
    width: 10px;
    border-radius: 5px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #7209B7, stop:1 #F72585);
    border-radius: 5px;
    min-height: 28px;
}
QScrollBar::handle:vertical:hover {
    background: #3A0CA3;
}
"""

METADATA_PANEL_STYLE = """
QWidget#metadataPanel {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #faf5ff, stop:1 #fff8fc);
    border-left: 3px solid #7209B7;
    border-radius: 12px;
}
"""

METADATA_CLOSE_BUTTON_STYLE = """
QPushButton#metadataCloseButton {
    color: #7209B7;
    font-size: 18px;
    font-weight: 700;
    background-color: transparent;
    border: none;
    border-radius: 14px;
    padding: 0;
}
QPushButton#metadataCloseButton:hover {
    color: #ffffff;
    background-color: #F72585;
}
QPushButton#metadataCloseButton:pressed {
    color: #ffffff;
    background-color: #560BAD;
}
"""

PREVIEW_LABEL_STYLE = """
QLabel#iconPreviewLabel {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #ffffff, stop:1 #f3eeff);
    border: 2px dashed #B5179E;
    border-radius: 10px;
    color: #560BAD;
    font-size: 12px;
    font-weight: 600;
    padding: 6px;
    margin: 0;
}
"""

METADATA_GROUP_STYLE = """
QGroupBox {
    font-size: 13px;
    font-weight: 700;
    color: #560BAD;
    border: 2px solid #C77DFF;
    border-radius: 12px;
    margin-top: 14px;
    padding: 10px 8px 8px 8px;
    background-color: rgba(255, 255, 255, 0.78);
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 8px;
    background-color: #faf5ff;
    color: #7209B7;
}
"""

FORMAT_GROUP_STYLE = """
QGroupBox#formatGroup {
    font-weight: 700;
    color: #9D0208;
    border: 2px solid #F72585;
    border-radius: 12px;
    margin-top: 12px;
    padding: 8px 8px 8px 8px;
    background-color: rgba(255, 255, 255, 0.82);
}
QGroupBox#formatGroup::title {
    color: #F72585;
    padding: 0 8px;
}
QRadioButton {
    font-size: 12px;
    font-weight: 600;
    color: #560BAD;
    spacing: 8px;
}
QRadioButton::indicator {
    width: 16px;
    height: 16px;
}
QRadioButton::indicator:checked {
    background-color: #CCFF33;
    border: 2px solid #7209B7;
    border-radius: 8px;
}
"""

METADATA_FIELD_LABEL_STYLE = """
QLabel {
    color: #3A0CA3;
    font-size: 11px;
    font-weight: 700;
    padding: 0px 0 0px 0px;
    margin-left: 0px;
}
"""

METADATA_VALUE_STYLE = """
QLabel {
    font-size: 11px;
    font-weight: 500;
    color: #1e1b2e;
    background-color: #ffffff;
    border: 1px solid #e9d5ff;
    border-radius: 8px;
    padding: 6px 8px;
}
"""

PRIMARY_TAG_VALUE_STYLE = """
QLabel {
    font-size: 11px;
    font-weight: 700;
    color: #560BAD;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #f3eeff, stop:0.5 #ffe3f1, stop:1 #f5ffd6);
    border: 1px solid #F72585;
    border-radius: 8px;
    padding: 6px 8px;
}
"""

SPLITTER_STYLE = """
QSplitter::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #3A0CA3, stop:0.35 #7209B7, stop:0.65 #F72585, stop:1 #CCFF33);
    width: 4px;
    margin: 10px 3px;
    border-radius: 2px;
}
"""

BUTTON_BOX_STYLE = """
QDialogButtonBox QPushButton {
    min-width: 92px;
    min-height: 34px;
    font-weight: 600;
    font-size: 12px;
    border-radius: 10px;
    padding: 6px 18px;
}
QDialogButtonBox QPushButton:default {
    background-color: #7209B7;
    color: #ffffff;
    border: 2px solid #560BAD;
}
QDialogButtonBox QPushButton:default:hover {
    background-color: #9D4EDD;
}
QDialogButtonBox QPushButton:!default {
    background-color: #ffffff;
    color: #560BAD;
    border: 2px solid #C77DFF;
}
QDialogButtonBox QPushButton:!default:hover {
    background-color: #f3eeff;
}
"""

LABEL_STYLE = """
QLabel {
    font-size: 11px;
    font-weight: 700;
    color: #560BAD;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #f3eeff, stop:1 #fff0f8);
    border: 1px solid #C77DFF;
    border-radius: 10px;
    padding: 2px 4px;
    min-height: 56px;
}
"""

ICON_BUTTON_STYLE = """
QPushButton {
    background: #ffffff;
    border: 2px solid #d8b4fe;
    border-radius: 14px;
    padding: 8px;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ede9fe, stop:1 #fce7f3);
    border: 2px solid #F72585;
}
QPushButton:checked {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #e0d4ff, stop:1 #ffd6ec);
    border: 3px solid #7209B7;
    border-radius: 14px;
}
QPushButton:pressed {
    background-color: #C77DFF;
    border: 3px solid #3A0CA3;
}
"""

CONTAINER_STYLE = """
QWidget {
    background-color: rgba(255, 255, 255, 0.5);
    border: 1px solid rgba(199, 125, 255, 0.45);
    border-radius: 14px;
    padding: 4px;
}
"""