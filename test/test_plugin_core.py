# coding=utf-8
"""
Unit tests for plugin config and data_manager (no QGIS required).

Run from repo root:
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

ROOT = Path(__file__).resolve().parent.parent

MOCK_ZENODO_API_RESPONSE = {
    "id": 20397958,
    "files": [
        {
            "key": "map-icon-metadata.csv",
            "links": {
                "download": "https://zenodo.org/records/20397958/files/map-icon-metadata.csv?download=1",
            },
        },
        {
            "key": "map-icon-png.zip",
            "links": {
                "download": "https://zenodo.org/records/20397958/files/map-icon-png.zip?download=1",
            },
        },
        {
            "key": "map-icon-svg.zip",
            "links": {
                "download": "https://zenodo.org/records/20397958/files/map-icon-svg.zip?download=1",
            },
        },
    ],
}


def _bootstrap_map_icons_package():
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
    pkg.config = config_mod

    spec_dm = importlib.util.spec_from_file_location(
        "map_icons.data_manager", ROOT / "data_manager.py"
    )
    dm_mod = importlib.util.module_from_spec(spec_dm)
    sys.modules["map_icons.data_manager"] = dm_mod
    spec_dm.loader.exec_module(dm_mod)
    pkg.data_manager = dm_mod


_bootstrap_map_icons_package()

from map_icons import config  # noqa: E402
from map_icons.data_manager import (  # noqa: E402
    DataManager,
    get_zenodo_assets,
    resolve_latest_zenodo_assets,
)


class TestConfig(unittest.TestCase):
    def test_zenodo_concept_doi(self):
        self.assertIn("zenodo", config.ZENODO_CONCEPT_DOI)
        self.assertEqual(config.ZENODO_DOI, config.ZENODO_CONCEPT_DOI)

    def test_zenodo_api_latest_url(self):
        self.assertTrue(config.ZENODO_API_LATEST_URL.startswith("https://"))
        self.assertIn(str(config.ZENODO_CONCEPT_RECID), config.ZENODO_API_LATEST_URL)

    def test_asset_filenames_v5(self):
        self.assertEqual(config.ZENODO_PNG_ZIP_NAME, "map-icon-png.zip")
        self.assertEqual(config.ZENODO_SVG_ZIP_NAME, "map-icon-svg.zip")
        self.assertEqual(config.ZENODO_METADATA_CSV_NAME, "map-icon-metadata.csv")

    def test_v5_folder_names(self):
        self.assertEqual(config.PNG_FOLDER, "map-icon-png")
        self.assertEqual(config.SVG_FOLDER, "map-icon-svg")

    def test_metadata_csv_headers_v5(self):
        self.assertIn("metadata-source", config.METADATA_CSV_HEADERS)
        self.assertIn("notes", config.METADATA_CSV_HEADERS)

    def test_ui_constants_sane(self):
        self.assertGreater(config.MAX_ICONS_PER_ROW, 0)
        self.assertGreater(config.ICON_SIZE, 0)


class TestZenodoApi(unittest.TestCase):
    def setUp(self):
        import map_icons.data_manager as dm_mod

        dm_mod._zenodo_assets = None

    @patch("map_icons.data_manager.requests")
    def test_resolve_latest_zenodo_assets(self, mock_requests_module):
        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_ZENODO_API_RESPONSE
        mock_resp.raise_for_status = MagicMock()
        mock_requests_module.get.return_value = mock_resp

        assets = resolve_latest_zenodo_assets()
        self.assertIsNotNone(assets)
        self.assertEqual(assets["record_id"], "20397958")
        self.assertIn("map-icon-png.zip", assets["png_zip_url"])

    @patch("map_icons.data_manager.requests")
    def test_get_zenodo_assets_caches_result(self, mock_requests_module):
        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_ZENODO_API_RESPONSE
        mock_resp.raise_for_status = MagicMock()
        mock_requests_module.get.return_value = mock_resp

        first = get_zenodo_assets(force_refresh=True)
        second = get_zenodo_assets()
        self.assertEqual(first, second)
        mock_requests_module.get.assert_called_once()


class TestDataManager(unittest.TestCase):
    def setUp(self):
        import map_icons.data_manager as dm_mod

        dm_mod._zenodo_assets = None
        self._tmp = tempfile.TemporaryDirectory()
        self.plugin_dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_init_creates_cache_dirs(self):
        dm = DataManager(str(self.plugin_dir))
        self.assertTrue(dm.cache_dir.is_dir())

    def test_get_metadata_file_uses_v5_name(self):
        dm = DataManager(str(self.plugin_dir))
        self.assertTrue(str(dm.get_metadata_file()).endswith("map-icon-metadata.csv"))

    def test_icons_exist_true_with_png_in_map_icon_png(self):
        dm = DataManager(str(self.plugin_dir))
        png_dir = dm.cache_dir / "map-icon-png"
        png_dir.mkdir(parents=True)
        (png_dir / "00e8059e.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)
        self.assertTrue(dm.icons_exist())

    def test_icons_exist_false_with_only_legacy_sample_icon_set(self):
        dm = DataManager(str(self.plugin_dir))
        legacy = dm.cache_dir / "sample-icon-set"
        legacy.mkdir(parents=True)
        (legacy / "1.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)
        self.assertFalse(dm.icons_exist())

    @patch("map_icons.data_manager.get_zenodo_assets")
    def test_refresh_cache_if_new_release_clears_cache(self, mock_get_assets):
        dm = DataManager(str(self.plugin_dir))
        png_dir = dm.cache_dir / "map-icon-png"
        png_dir.mkdir(parents=True)
        (png_dir / "00e8059e.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)
        dm._write_cached_record_id("20126394")

        mock_get_assets.return_value = {
            "record_id": "20397958",
            "png_zip_url": "https://example.com/map-icon-png.zip",
            "svg_zip_url": "https://example.com/map-icon-svg.zip",
            "metadata_csv_url": "https://example.com/map-icon-metadata.csv",
            "metadata_filename": "map-icon-metadata.csv",
        }

        self.assertTrue(dm._refresh_cache_if_new_release())
        self.assertFalse((dm.cache_dir / "map-icon-png" / "00e8059e.png").exists())
    def test_metadata_exists_true_when_file_present(self):
        dm = DataManager(str(self.plugin_dir))
        p = dm.get_metadata_file()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"dummy")
        self.assertTrue(dm.metadata_exists())

    def test_check_dependencies_structure(self):
        dm = DataManager(str(self.plugin_dir))
        deps = dm.check_dependencies()
        self.assertIn("urllib", deps)
        self.assertIn("zipfile", deps)
        self.assertTrue(deps["urllib"])
        self.assertTrue(deps["zipfile"])

    @patch("map_icons.data_manager.urlopen")
    def test_download_file_success(self, mock_urlopen):
        from io import BytesIO

        dm = DataManager(str(self.plugin_dir))
        mock_response = MagicMock()
        mock_response.__enter__ = MagicMock(return_value=BytesIO(b"data"))
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        out = self.plugin_dir / "cache" / "icons" / "downloaded.bin"
        out.parent.mkdir(parents=True, exist_ok=True)
        ok = dm.download_file("https://example.com/file", out, "test")

        self.assertTrue(ok)
        self.assertTrue(out.exists())
        self.assertEqual(out.read_bytes(), b"data")

    @patch("map_icons.data_manager.urlopen")
    def test_download_file_http_error(self, mock_urlopen):
        from urllib.error import HTTPError

        dm = DataManager(str(self.plugin_dir))
        mock_urlopen.side_effect = HTTPError(
            "https://example.com/x", 404, "Not Found", hdrs=None, fp=None
        )
        out = self.plugin_dir / "cache" / "icons" / "x.bin"
        out.parent.mkdir(parents=True, exist_ok=True)
        ok = dm.download_file("https://example.com/x", out, "x")
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
