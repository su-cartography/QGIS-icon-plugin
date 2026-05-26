# coding=utf-8
"""
Unit tests for plugin config and data_manager (no QGIS required).

Run from repo root:
    python test/test_plugin_core.py

Or with unittest discovery (loads test/__init__.py which needs qgis — avoid):
    python test/test_plugin_core.py
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Repo root = parent of test/
ROOT = Path(__file__).resolve().parent.parent


def _bootstrap_map_icons_package():
    """
    Load the plugin as package 'map_icons' so data_manager's relative imports work.
    """
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    if "map_icons" in sys.modules and hasattr(sys.modules["map_icons"], "data_manager"):
        return

    pkg = types.ModuleType("map_icons")
    pkg.__path__ = [str(ROOT)]
    sys.modules["map_icons"] = pkg

    spec_c = importlib.util.spec_from_file_location(
        "map_icons.config", ROOT / "config.py"
    )
    config_mod = importlib.util.module_from_spec(spec_c)
    sys.modules["map_icons.config"] = config_mod
    spec_c.loader.exec_module(config_mod)

    spec_dm = importlib.util.spec_from_file_location(
        "map_icons.data_manager", ROOT / "data_manager.py"
    )
    dm_mod = importlib.util.module_from_spec(spec_dm)
    sys.modules["map_icons.data_manager"] = dm_mod
    spec_dm.loader.exec_module(dm_mod)


_bootstrap_map_icons_package()

from map_icons import config  # noqa: E402
from map_icons.data_manager import DataManager  # noqa: E402


class TestConfig(unittest.TestCase):
    """Zenodo URLs and constants stay internally consistent."""

    def test_zenodo_doi_format(self):
        self.assertIn("zenodo", config.ZENODO_DOI)
        self.assertIn(".", config.ZENODO_DOI)

    def test_zenodo_urls_https_and_record(self):
        self.assertTrue(config.ZENODO_BASE_URL.startswith("https://"))
        self.assertIn("20126394", config.ZENODO_BASE_URL)

    def test_asset_urls_under_base(self):
        self.assertTrue(config.ICONS_ZIP_URL.startswith(config.ZENODO_BASE_URL))
        self.assertTrue(config.SVG_ZIP_URL.startswith(config.ZENODO_BASE_URL))
        self.assertTrue(config.METADATA_FILE_URL.startswith(config.ZENODO_BASE_URL))
        self.assertEqual(config.METADATA_EXCEL_URL, config.METADATA_FILE_URL)

    def test_zip_and_metadata_filenames(self):
        self.assertIn("sample-icon-set-PNG.zip", config.ICONS_ZIP_URL)
        self.assertIn("sample-icon-set-SVG.zip", config.SVG_ZIP_URL)
        self.assertIn("sample-icon-set-metadata.csv", config.METADATA_FILE_URL)

    def test_ui_constants_sane(self):
        self.assertGreater(config.MAX_ICONS_PER_ROW, 0)
        self.assertGreater(config.ICON_SIZE, 0)
        self.assertGreater(config.BUTTON_SIZE, 0)


class TestDataManager(unittest.TestCase):
    """DataManager paths and cache detection without network."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.plugin_dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_init_creates_cache_dirs(self):
        dm = DataManager(str(self.plugin_dir))
        self.assertTrue(dm.cache_dir.is_dir())
        self.assertTrue(dm.icons_cache_dir.is_dir())
        self.assertTrue(dm.metadata_cache_dir.is_dir())

    def test_get_metadata_file_name_from_url(self):
        dm = DataManager(str(self.plugin_dir))
        p = dm.get_metadata_file()
        self.assertTrue(str(p).endswith("sample-icon-set-metadata.csv"))
        self.assertEqual(p.parent, dm.metadata_cache_dir)

    def test_icons_exist_false_when_empty(self):
        dm = DataManager(str(self.plugin_dir))
        self.assertFalse(dm.icons_exist())

    def test_icons_exist_false_with_only_legacy_sample_icon_set(self):
        """Old cache/sample-icon-set/1.png does not count; only sample-icon-set-PNG/."""
        dm = DataManager(str(self.plugin_dir))
        legacy = dm.cache_dir / "sample-icon-set"
        legacy.mkdir(parents=True)
        (legacy / "1.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)
        self.assertFalse(dm.icons_exist())

    def test_icons_exist_true_with_png_in_sample_icon_set_png(self):
        dm = DataManager(str(self.plugin_dir))
        png_dir = dm.cache_dir / "sample-icon-set-PNG"
        png_dir.mkdir(parents=True)
        (png_dir / "00e8059e.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)
        self.assertTrue(dm.icons_exist())

    def test_svgs_exist_false_when_empty(self):
        dm = DataManager(str(self.plugin_dir))
        self.assertFalse(dm.svgs_exist())

    def test_svgs_exist_true_with_svg_in_sample_icon_set_svg(self):
        dm = DataManager(str(self.plugin_dir))
        svg_dir = dm.cache_dir / "sample-icon-set-SVG"
        svg_dir.mkdir(parents=True)
        (svg_dir / "00e8059e.svg").write_text(
            "<svg xmlns='http://www.w3.org/2000/svg'/>", encoding="utf-8"
        )
        self.assertTrue(dm.svgs_exist())

    def test_metadata_exists_false_without_file(self):
        dm = DataManager(str(self.plugin_dir))
        self.assertFalse(dm.metadata_exists())

    def test_metadata_exists_true_when_file_present(self):
        dm = DataManager(str(self.plugin_dir))
        p = dm.get_metadata_file()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"dummy")
        self.assertTrue(dm.metadata_exists())

    def test_check_dependencies_structure(self):
        dm = DataManager(str(self.plugin_dir))
        deps = dm.check_dependencies()
        self.assertIn("requests", deps)
        self.assertIn("openpyxl", deps)
        self.assertIn("zipfile", deps)
        self.assertTrue(deps["zipfile"])

    @patch("map_icons.data_manager.requests")
    def test_download_file_success(self, mock_requests_module):
        dm = DataManager(str(self.plugin_dir))
        mock_resp = MagicMock()
        mock_resp.iter_content.return_value = [b"data"]
        mock_resp.raise_for_status = MagicMock()
        mock_requests_module.get.return_value = mock_resp

        out = self.plugin_dir / "cache" / "icons" / "downloaded.bin"
        out.parent.mkdir(parents=True, exist_ok=True)
        ok = dm.download_file("https://example.com/file", out, "test")

        self.assertTrue(ok)
        self.assertTrue(out.exists())
        self.assertEqual(out.read_bytes(), b"data")

    @patch("map_icons.data_manager.requests", None)
    @patch("map_icons.data_manager.REQUESTS_AVAILABLE", False)
    def test_download_file_no_requests(self):
        dm = DataManager(str(self.plugin_dir))
        out = self.plugin_dir / "cache" / "icons" / "x.bin"
        out.parent.mkdir(parents=True, exist_ok=True)
        ok = dm.download_file("https://example.com/x", out, "x")
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
