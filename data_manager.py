# -*- coding: utf-8 -*-
"""
Data Manager for Map Icons QGIS Plugin

Downloads and caches icons, SVGs, and metadata from Zenodo.
"""

import logging
import shutil
import zipfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .config import (
    ICONS_ZIP_URL,
    SVG_ZIP_URL,
    METADATA_FILE_URL,
    CACHE_DIR,
    ICONS_CACHE_DIR,
    METADATA_CACHE_DIR,
    PNG_FOLDER,
    SVG_FOLDER,
)

logger = logging.getLogger(__name__)

_USER_AGENT = "Map-Icons-QGIS-Plugin"


def _zip_basename(url):
    return urlparse(url).path.rsplit("/", 1)[-1]


def _is_junk_svg(path):
    return "__MACOSX" in path.parts or path.name.startswith("._")


def _download(url, dest, label):
    """Download url to dest using urllib.request. Returns True on success."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        logger.info("Downloading %s from %s", label, url)
        request = Request(url, headers={"User-Agent": _USER_AGENT})
        with urlopen(request, timeout=30) as response:
            with open(dest, "wb") as f:
                shutil.copyfileobj(response, f)
        logger.info("Downloaded %s to %s", label, dest)
        return True
    except (HTTPError, URLError, OSError, TimeoutError) as err:
        logger.error("Failed to download %s: %s", label, err)
        return False


def _extract_zip(zip_path, extract_to, label):
    """Extract zip_path into extract_to, then delete the zip. Returns True on success."""
    zip_path = Path(zip_path)
    extract_to = Path(extract_to)
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_to)
        zip_path.unlink(missing_ok=True)
        logger.info("Extracted %s", label)
        return True
    except (zipfile.BadZipFile, OSError) as err:
        logger.error("Failed to extract %s: %s", label, err)
        return False


def _copy_svgs_into_png_folder(cache_dir, png_dir):
    """Copy extracted SVGs beside PNGs (same unique-ID filename). Returns copy count."""
    png_dir = Path(png_dir)
    png_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    for svg_path in Path(cache_dir).rglob("*.svg"):
        if _is_junk_svg(svg_path):
            continue
        dest = png_dir / svg_path.name
        if dest == svg_path:
            continue
        if dest.exists() and dest.stat().st_mtime >= svg_path.stat().st_mtime:
            continue
        try:
            shutil.copy2(svg_path, dest)
            copied += 1
        except OSError as err:
            logger.warning("Could not copy %s to %s: %s", svg_path, png_dir, err)
    if copied:
        logger.info("Copied %s SVG file(s) into %s", copied, png_dir)
    return copied


def _remove_tree(path):
    """Delete a directory tree. Returns True on success."""
    path = Path(path)
    if not path.exists():
        return True
    try:
        shutil.rmtree(path)
        logger.info("Cache cleared: %s", path)
        return True
    except OSError as err:
        logger.error("Failed to clear cache %s: %s", path, err)
        return False


class DataManager:
    """Manages downloading and caching of plugin data from Zenodo."""

    def __init__(self, plugin_dir):
        """Set cache paths under the plugin directory and create cache folders."""
        self.plugin_dir = Path(plugin_dir)
        self.cache_dir = self.plugin_dir / CACHE_DIR
        self.icons_cache_dir = self.plugin_dir / ICONS_CACHE_DIR
        self.metadata_cache_dir = self.plugin_dir / METADATA_CACHE_DIR
        for d in (self.cache_dir, self.icons_cache_dir, self.metadata_cache_dir):
            d.mkdir(parents=True, exist_ok=True)

    def download_file(self, url, local_path, description="file"):
        """Download a file from a URL into local_path. Returns True on success."""
        return _download(url, local_path, description)

    def _download_and_extract(self, url, label):
        """Download a Zenodo zip and extract it under cache/."""
        zip_path = self.icons_cache_dir / _zip_basename(url)
        if not _download(url, zip_path, f"{label} zip"):
            return False
        return _extract_zip(zip_path, self.cache_dir, label)

    def download_and_extract_icons(self):
        """Download and extract map-icon-png.zip from Zenodo."""
        return self._download_and_extract(ICONS_ZIP_URL, "icons")

    def download_and_extract_svgs(self):
        """Download SVG zip, extract it, and copy SVGs beside PNGs in map-icon-png/."""
        if not self._download_and_extract(SVG_ZIP_URL, "SVG icons"):
            return False
        _copy_svgs_into_png_folder(self.cache_dir, self.cache_dir / PNG_FOLDER)
        return True

    def download_metadata(self):
        """Download map-icon-metadata.csv from Zenodo into the metadata cache."""
        path = self.metadata_cache_dir / _zip_basename(METADATA_FILE_URL)
        return _download(METADATA_FILE_URL, path, "metadata file")

    def get_icons_directory(self):
        """Return the path where icon zip files are stored during download."""
        return self.icons_cache_dir

    def get_metadata_file(self):
        """Return the path to the cached metadata CSV file."""
        return self.metadata_cache_dir / _zip_basename(METADATA_FILE_URL)

    def get_png_icons_directory(self):
        """Return the cache folder containing PNG icons, or None if not found."""
        png_dir = self.cache_dir / PNG_FOLDER
        if png_dir.is_dir() and any(png_dir.glob("*.png")):
            return png_dir
        return None

    def get_svg_search_directories(self):
        """Return cache folders that may contain SVG files."""
        dirs = []
        for name in (SVG_FOLDER, PNG_FOLDER):
            folder = self.cache_dir / name
            if folder.is_dir():
                dirs.append(folder)
        return dirs

    def icons_exist(self):
        """True if hash-named PNGs exist under cache/map-icon-png/."""
        return self.get_png_icons_directory() is not None

    def svgs_exist(self):
        """True if SVG files exist in map-icon-svg or beside PNGs."""
        for folder in self.get_svg_search_directories():
            if any(p for p in folder.glob("*.svg") if not p.name.startswith("._")):
                return True
        return False

    def metadata_exists(self):
        """True if the metadata CSV has been downloaded."""
        return self.get_metadata_file().is_file()

    def ensure_data_available(self):
        """Download PNGs, SVGs, and metadata from Zenodo if any are missing from cache."""
        ok = True
        if not self.icons_exist():
            logger.info("Icons not in cache, downloading from Zenodo...")
            ok = self.download_and_extract_icons() and ok
        if not self.svgs_exist():
            logger.info("SVG icons not in cache, downloading from Zenodo...")
            if not self.download_and_extract_svgs():
                logger.warning("SVG download failed; continuing without SVGs")
        if not self.metadata_exists():
            logger.info("Metadata not in cache, downloading from Zenodo...")
            ok = self.download_metadata() and ok
        return ok

    def clear_cache(self):
        """Remove the entire plugin cache directory."""
        _remove_tree(self.cache_dir)

    def get_cache_info(self):
        """Return icon count, metadata presence, and cache path for debugging."""
        png_dir = self.get_png_icons_directory()
        icons = list(png_dir.glob("*.png")) if png_dir is not None else []
        return {
            "cache_dir": str(self.cache_dir),
            "icons_count": len(icons),
            "metadata_exists": self.metadata_exists(),
            "total_size": sum(f.stat().st_size for f in icons),
        }

    def check_dependencies(self):
        """Report whether stdlib modules used by the plugin are available."""
        return {
            "urllib": True,
            "zipfile": True,
        }

    def get_installation_instructions(self):
        """Return pip install hints for any missing optional dependencies."""
        return "All dependencies are available!"
