# -*- coding: utf-8 -*-
"""
Data Manager for Map Icons QGIS Plugin

Downloads and caches icons, SVGs, and metadata from Zenodo.
"""

import json
import logging
import shutil
import zipfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .config import (
    CACHE_DIR,
    ICONS_CACHE_DIR,
    METADATA_CACHE_DIR,
    PNG_FOLDER,
    SVG_FOLDER,
    ZENODO_API_LATEST_URL,
    ZENODO_METADATA_CSV_NAME,
    ZENODO_PNG_ZIP_NAME,
    ZENODO_RECORD_ID_FILE,
    ZENODO_SVG_ZIP_NAME,
)

logger = logging.getLogger(__name__)

_USER_AGENT = "Map-Icons-QGIS-Plugin"
_zenodo_assets = None

def _zip_basename(url):
    return urlparse(url).path.rsplit("/", 1)[-1]


def _is_junk_svg(path):
    return "__MACOSX" in path.parts or path.name.startswith("._")


def _pick_file(files, filename):
    """Return the download URL for an exact filename in a Zenodo files list."""
    for entry in files:
        if entry.get("key") == filename:
            links = entry.get("links") or {}
            return links.get("download") or links.get("self")
    return None


def resolve_latest_zenodo_assets():
    """
    Query Zenodo for the latest release and resolve download URLs.

    Returns a dict with record_id and asset URLs, or None if the API call fails.
    """
    try:
        logger.info("Fetching latest Zenodo record from %s", ZENODO_API_LATEST_URL)
        request = Request(
            ZENODO_API_LATEST_URL, headers={"User-Agent": _USER_AGENT}
        )
        with urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, OSError, TimeoutError, ValueError, json.JSONDecodeError) as err:
        logger.error("Failed to fetch Zenodo API: %s", err)
        return None

    record_id = str(payload.get("id", ""))
    files = payload.get("files") or []
    png_url = _pick_file(files, ZENODO_PNG_ZIP_NAME)
    svg_url = _pick_file(files, ZENODO_SVG_ZIP_NAME)
    metadata_url = _pick_file(files, ZENODO_METADATA_CSV_NAME)

    missing = [
        name
        for name, url in (
            (ZENODO_PNG_ZIP_NAME, png_url),
            (ZENODO_SVG_ZIP_NAME, svg_url),
            (ZENODO_METADATA_CSV_NAME, metadata_url),
        )
        if not url
    ]
    if missing:
        logger.error("Zenodo record %s is missing expected files: %s", record_id, missing)
        return None

    assets = {
        "record_id": record_id,
        "png_zip_url": png_url,
        "svg_zip_url": svg_url,
        "metadata_csv_url": metadata_url,
        "metadata_filename": ZENODO_METADATA_CSV_NAME,
    }
    logger.info("Resolved Zenodo record %s assets", record_id)
    return assets


def get_zenodo_assets(force_refresh=False):
    """Return cached Zenodo asset URLs, refreshing from the API when needed."""
    global _zenodo_assets
    if force_refresh or _zenodo_assets is None:
        _zenodo_assets = resolve_latest_zenodo_assets()
    return _zenodo_assets


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
        self.zenodo_record_id_file = self.plugin_dir / ZENODO_RECORD_ID_FILE
        for d in (self.cache_dir, self.icons_cache_dir, self.metadata_cache_dir):
            d.mkdir(parents=True, exist_ok=True)

    def _read_cached_record_id(self):
        try:
            return self.zenodo_record_id_file.read_text(encoding="utf-8").strip()
        except OSError:
            return ""

    def _write_cached_record_id(self, record_id):
        self.zenodo_record_id_file.parent.mkdir(parents=True, exist_ok=True)
        self.zenodo_record_id_file.write_text(str(record_id), encoding="utf-8")

    def _cache_has_data(self):
        return self.icons_exist() or self.svgs_exist() or self.metadata_exists()

    def _refresh_cache_if_new_release(self):
        """
        Clear cache when Zenodo publishes a newer record than the one cached.

        Returns True if assets were resolved or cached data can be used offline.
        """
        assets = get_zenodo_assets(force_refresh=True)
        if assets is None:
            if self._cache_has_data():
                logger.warning(
                    "Zenodo API unavailable; continuing with cached data if present"
                )
                return True
            return False

        latest_id = assets["record_id"]
        cached_id = self._read_cached_record_id()
        if cached_id and cached_id != latest_id:
            logger.info(
                "New Zenodo release detected (%s -> %s); clearing cache",
                cached_id,
                latest_id,
            )
            self.clear_cache(keep_record_id=False)
        return True

    def _current_assets(self):
        assets = get_zenodo_assets()
        if assets is None and self._cache_has_data():
            logger.warning("Using cached data without refreshed Zenodo asset URLs")
        return assets

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
        """Download and extract the PNG zip from the latest Zenodo record."""
        assets = self._current_assets()
        if not assets:
            return False
        return self._download_and_extract(assets["png_zip_url"], "icons")

    def download_and_extract_svgs(self):
        """Download SVG zip, extract it, and copy SVGs beside PNGs."""
        assets = self._current_assets()
        if not assets:
            return False
        if not self._download_and_extract(assets["svg_zip_url"], "SVG icons"):
            return False
        png_dir = self.get_png_icons_directory()
        if png_dir is not None:
            _copy_svgs_into_png_folder(self.cache_dir, png_dir)
        else:
            _copy_svgs_into_png_folder(self.cache_dir, self.cache_dir / PNG_FOLDER)
        return True

    def download_metadata(self):
        """Download the metadata CSV from the latest Zenodo record."""
        assets = self._current_assets()
        if not assets:
            return False
        path = self.metadata_cache_dir / assets["metadata_filename"]
        return _download(assets["metadata_csv_url"], path, "metadata file")

    def get_icons_directory(self):
        """Return the path where icon zip files are stored during download."""
        return self.icons_cache_dir

    def get_metadata_file(self):
        """Return the path to the cached metadata CSV file."""
        assets = get_zenodo_assets()
        filename = (
            assets["metadata_filename"]
            if assets
            else ZENODO_METADATA_CSV_NAME
        )
        return self.metadata_cache_dir / filename

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
        if not self._refresh_cache_if_new_release():
            return False

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
        if ok:
            assets = get_zenodo_assets()
            if assets:
                self._write_cached_record_id(assets["record_id"])
        return ok

    def clear_cache(self, keep_record_id=False):
        """Remove the plugin cache directory and reset resolved Zenodo assets."""
        global _zenodo_assets
        record_file = self.zenodo_record_id_file
        _remove_tree(self.cache_dir)
        _zenodo_assets = None
        if not keep_record_id and record_file.exists():
            try:
                record_file.unlink()
            except OSError as err:
                logger.warning("Could not remove %s: %s", record_file, err)
        for d in (self.cache_dir, self.icons_cache_dir, self.metadata_cache_dir):
            d.mkdir(parents=True, exist_ok=True)

    def get_cache_info(self):
        """Return icon count, metadata presence, and cache path for debugging."""
        png_dir = self.get_png_icons_directory()
        icons = list(png_dir.glob("*.png")) if png_dir is not None else []
        assets = get_zenodo_assets()
        return {
            "cache_dir": str(self.cache_dir),
            "icons_count": len(icons),
            "metadata_exists": self.metadata_exists(),
            "total_size": sum(f.stat().st_size for f in icons),
            "zenodo_record_id": self._read_cached_record_id(),
            "zenodo_latest_record_id": assets["record_id"] if assets else None,
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