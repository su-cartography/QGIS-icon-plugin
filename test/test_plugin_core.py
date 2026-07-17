# coding=utf-8
"""
Unit tests for plugin config and data_manager (no QGIS required).

Covers Zenodo latest-release API,  asset/metadata naming, cache refresh,
and UI.

Run from repo root:
    python test/test_plugin_core.py
"""
from __future__ import annotations

import importlib.util
import json
import logging
import sys
import tempfile
import types
import unittest
import zipfile
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parent.parent

MOCK_ZENODO_API_RESPONSE = {
    "id": 20397958,
    "files": [
        {
            "key": "map-icon-metadata.csv",
            "links": {
                "download": (
                    "https://zenodo.org/records/20397958/files/"
                    "map-icon-metadata.csv?download=1"
                ),
            },
        },
        {
            "key": "map-icon-png.zip",
            "links": {
                "download": (
                    "https://zenodo.org/records/20397958/files/"
                    "map-icon-png.zip?download=1"
                ),
            },
        },
        {
            "key": "map-icon-svg.zip",
            "links": {
                "download": (
                    "https://zenodo.org/records/20397958/files/"
                    "map-icon-svg.zip?download=1"
                ),
            },
        },
    ],
}


def _mock_urlopen_json(payload):
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(payload).encode("utf-8")
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=False)
    return mock_response


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

# Silence expected error logs from intentional failure tests
logging.getLogger("map_icons.data_manager").setLevel(logging.CRITICAL)

from map_icons import config  # noqa: E402
from map_icons.data_manager import (  # noqa: E402
    DataManager,
    _extract_zip,
    _is_junk_svg,
    _pick_file,
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
        self.assertIn("unique-ID", config.METADATA_CSV_HEADERS)
        self.assertIn("metadata-source", config.METADATA_CSV_HEADERS)
        self.assertIn("notes", config.METADATA_CSV_HEADERS)
        self.assertNotIn("metadata", config.METADATA_CSV_HEADERS)

    def test_metadata_csv_headers_v5_extended_fields(self):
        for column in (
            "creation-context",
            "icon-context",
            "icon-description",
            "icon-geography",
            "designer",
            "uploader",
            "primary-tags",
            "secondary-tags",
        ):
            self.assertIn(column, config.METADATA_CSV_HEADERS)

    def test_plugin_icon_file_exists(self):
        icon_path = ROOT / config.PLUGIN_ICON_FILENAME
        self.assertTrue(icon_path.is_file(), f"Missing plugin icon: {icon_path}")

    def test_metadata_preview_constants(self):
        self.assertGreater(config.METADATA_PREVIEW_SIZE, 0)
        self.assertGreaterEqual(
            config.METADATA_PREVIEW_HEIGHT, config.METADATA_PREVIEW_SIZE
        )

    def test_ui_constants_sane(self):
        self.assertGreater(config.MAX_ICONS_PER_ROW, 0)
        self.assertGreater(config.ICON_SIZE, 0)
        self.assertGreaterEqual(config.BUTTON_SIZE, config.ICON_SIZE)
        self.assertGreater(config.LABEL_MAX_WIDTH, 0)
        self.assertGreater(config.LABEL_MIN_HEIGHT, 0)

    def test_ui_theme_styles_present(self):
        for name in (
            "DIALOG_STYLE",
            "HEADER_STYLE",
            "SEARCH_STYLE",
            "METADATA_PANEL_STYLE",
            "METADATA_GROUP_STYLE",
            "METADATA_VALUE_STYLE",
            "METADATA_CLOSE_BUTTON_STYLE",
            "LABEL_STYLE",
            "ICON_BUTTON_STYLE",
            "CONTAINER_STYLE",
            "BUTTON_BOX_STYLE",
            "SPLITTER_STYLE",
        ):
            style = getattr(config, name, "")
            self.assertTrue(style.strip(), f"{name} should be a non-empty stylesheet")


class TestZenodoHelpers(unittest.TestCase):
    """Pure helpers used when resolving Zenodo file lists."""

    def test_pick_file_exact_key(self):
        files = MOCK_ZENODO_API_RESPONSE["files"]
        url = _pick_file(files, "map-icon-png.zip")
        self.assertIsNotNone(url)
        self.assertIn("map-icon-png.zip", url)

    def test_pick_file_missing_returns_none(self):
        self.assertIsNone(_pick_file([], "map-icon-png.zip"))
        self.assertIsNone(
            _pick_file(MOCK_ZENODO_API_RESPONSE["files"], "wrong-name.zip")
        )

    def test_is_junk_svg_filters_macos_artifacts(self):
        self.assertTrue(_is_junk_svg(Path("__MACOSX/._foo.svg")))
        self.assertTrue(_is_junk_svg(Path("map-icon-svg/._hidden.svg")))
        self.assertFalse(_is_junk_svg(Path("map-icon-svg/00e8059e.svg")))


class TestZenodoApi(unittest.TestCase):
    def setUp(self):
        import map_icons.data_manager as dm_mod

        dm_mod._zenodo_assets = None

    @patch("map_icons.data_manager.urlopen")
    def test_resolve_latest_zenodo_assets(self, mock_urlopen):
        mock_urlopen.return_value = _mock_urlopen_json(MOCK_ZENODO_API_RESPONSE)

        assets = resolve_latest_zenodo_assets()
        self.assertIsNotNone(assets)
        self.assertEqual(assets["record_id"], "20397958")
        self.assertIn("map-icon-png.zip", assets["png_zip_url"])
        self.assertIn("map-icon-svg.zip", assets["svg_zip_url"])
        self.assertIn("map-icon-metadata.csv", assets["metadata_csv_url"])
        self.assertEqual(assets["metadata_filename"], "map-icon-metadata.csv")

    @patch("map_icons.data_manager.urlopen")
    def test_resolve_latest_zenodo_assets_missing_file(self, mock_urlopen):
        incomplete = {
            "id": 20397958,
            "files": [MOCK_ZENODO_API_RESPONSE["files"][0]],
        }
        mock_urlopen.return_value = _mock_urlopen_json(incomplete)

        self.assertIsNone(resolve_latest_zenodo_assets())

    @patch("map_icons.data_manager.urlopen")
    def test_resolve_latest_zenodo_assets_http_error(self, mock_urlopen):
        mock_urlopen.side_effect = HTTPError(
            "https://zenodo.org/api/records/x", 500, "Error", hdrs=None, fp=None
        )
        self.assertIsNone(resolve_latest_zenodo_assets())

    @patch("map_icons.data_manager.urlopen")
    def test_get_zenodo_assets_caches_result(self, mock_urlopen):
        mock_urlopen.return_value = _mock_urlopen_json(MOCK_ZENODO_API_RESPONSE)

        first = get_zenodo_assets(force_refresh=True)
        second = get_zenodo_assets()
        self.assertEqual(first, second)
        mock_urlopen.assert_called_once()

    @patch("map_icons.data_manager.urlopen")
    def test_get_zenodo_assets_force_refresh(self, mock_urlopen):
        mock_urlopen.return_value = _mock_urlopen_json(MOCK_ZENODO_API_RESPONSE)

        get_zenodo_assets(force_refresh=True)
        get_zenodo_assets(force_refresh=True)
        self.assertEqual(mock_urlopen.call_count, 2)


class TestExtractAndHelpers(unittest.TestCase):
    def test_extract_zip_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            zip_path = tmp_path / "bundle.zip"
            extract_to = tmp_path / "out"
            with zipfile.ZipFile(zip_path, "w") as zf:
                zf.writestr("map-icon-png/sample.png", b"\x89PNG")

            self.assertTrue(_extract_zip(zip_path, extract_to, "icons"))
            self.assertTrue((extract_to / "map-icon-png" / "sample.png").is_file())
            self.assertFalse(zip_path.exists())

    def test_extract_zip_bad_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            zip_path = tmp_path / "bad.zip"
            zip_path.write_bytes(b"not-a-zip")
            self.assertFalse(_extract_zip(zip_path, tmp_path / "out", "icons"))


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
        self.assertTrue(dm.icons_cache_dir.is_dir())
        self.assertTrue(dm.metadata_cache_dir.is_dir())

    def test_get_metadata_file_uses_v5_name(self):
        dm = DataManager(str(self.plugin_dir))
        p = dm.get_metadata_file()
        self.assertTrue(str(p).endswith("map-icon-metadata.csv"))
        self.assertEqual(p.parent, dm.metadata_cache_dir)

    def test_icons_exist_true_with_png_in_map_icon_png(self):
        dm = DataManager(str(self.plugin_dir))
        png_dir = dm.cache_dir / "map-icon-png"
        png_dir.mkdir(parents=True)
        (png_dir / "00e8059e.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)
        self.assertTrue(dm.icons_exist())
        self.assertEqual(dm.get_png_icons_directory(), png_dir)

    def test_icons_exist_false_with_only_legacy_sample_icon_set(self):
        """Old cache/sample-icon-set/1.png does not count; only map-icon-png/."""
        dm = DataManager(str(self.plugin_dir))
        legacy = dm.cache_dir / "sample-icon-set"
        legacy.mkdir(parents=True)
        (legacy / "1.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)
        self.assertFalse(dm.icons_exist())

    def test_svgs_exist_false_when_empty(self):
        dm = DataManager(str(self.plugin_dir))
        self.assertFalse(dm.svgs_exist())

    def test_svgs_exist_true_with_svg_in_map_icon_svg(self):
        dm = DataManager(str(self.plugin_dir))
        svg_dir = dm.cache_dir / "map-icon-svg"
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
        p.write_text("unique-ID,designer\n", encoding="utf-8")
        self.assertTrue(dm.metadata_exists())

    def test_get_svg_search_directories(self):
        dm = DataManager(str(self.plugin_dir))
        png_dir = dm.cache_dir / "map-icon-png"
        svg_dir = dm.cache_dir / "map-icon-svg"
        png_dir.mkdir(parents=True)
        svg_dir.mkdir(parents=True)
        dirs = dm.get_svg_search_directories()
        self.assertIn(svg_dir, dirs)
        self.assertIn(png_dir, dirs)

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

    @patch("map_icons.data_manager.get_zenodo_assets")
    def test_refresh_cache_same_release_keeps_cache(self, mock_get_assets):
        dm = DataManager(str(self.plugin_dir))
        png_dir = dm.cache_dir / "map-icon-png"
        png_dir.mkdir(parents=True)
        icon = png_dir / "00e8059e.png"
        icon.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)
        dm._write_cached_record_id("20397958")

        mock_get_assets.return_value = {
            "record_id": "20397958",
            "png_zip_url": "https://example.com/map-icon-png.zip",
            "svg_zip_url": "https://example.com/map-icon-svg.zip",
            "metadata_csv_url": "https://example.com/map-icon-metadata.csv",
            "metadata_filename": "map-icon-metadata.csv",
        }

        self.assertTrue(dm._refresh_cache_if_new_release())
        self.assertTrue(icon.exists())

    @patch("map_icons.data_manager.get_zenodo_assets")
    def test_refresh_cache_api_fail_with_cache_still_ok(self, mock_get_assets):
        dm = DataManager(str(self.plugin_dir))
        png_dir = dm.cache_dir / "map-icon-png"
        png_dir.mkdir(parents=True)
        (png_dir / "00e8059e.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)
        mock_get_assets.return_value = None

        self.assertTrue(dm._refresh_cache_if_new_release())

    @patch("map_icons.data_manager.get_zenodo_assets")
    def test_refresh_cache_api_fail_without_cache(self, mock_get_assets):
        dm = DataManager(str(self.plugin_dir))
        mock_get_assets.return_value = None
        self.assertFalse(dm._refresh_cache_if_new_release())

    @patch("map_icons.data_manager.get_zenodo_assets")
    def test_ensure_data_available_uses_existing_cache(self, mock_get_assets):
        mock_get_assets.return_value = {
            "record_id": "20397958",
            "png_zip_url": "https://example.com/map-icon-png.zip",
            "svg_zip_url": "https://example.com/map-icon-svg.zip",
            "metadata_csv_url": "https://example.com/map-icon-metadata.csv",
            "metadata_filename": "map-icon-metadata.csv",
        }
        dm = DataManager(str(self.plugin_dir))
        png_dir = dm.cache_dir / "map-icon-png"
        svg_dir = dm.cache_dir / "map-icon-svg"
        png_dir.mkdir(parents=True)
        svg_dir.mkdir(parents=True)
        (png_dir / "00e8059e.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)
        (svg_dir / "00e8059e.svg").write_text("<svg/>", encoding="utf-8")
        meta = dm.get_metadata_file()
        meta.parent.mkdir(parents=True, exist_ok=True)
        meta.write_text("unique-ID,designer\n", encoding="utf-8")

        self.assertTrue(dm.ensure_data_available())
        self.assertEqual(dm._read_cached_record_id(), "20397958")

    def test_clear_cache_removes_icons_and_resets_dirs(self):
        dm = DataManager(str(self.plugin_dir))
        png_dir = dm.cache_dir / "map-icon-png"
        png_dir.mkdir(parents=True)
        (png_dir / "00e8059e.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)
        dm._write_cached_record_id("20397958")

        dm.clear_cache(keep_record_id=False)

        self.assertFalse((dm.cache_dir / "map-icon-png" / "00e8059e.png").exists())
        self.assertTrue(dm.cache_dir.is_dir())
        self.assertEqual(dm._read_cached_record_id(), "")

    @patch("map_icons.data_manager.get_zenodo_assets")
    def test_get_cache_info_structure(self, mock_get_assets):
        mock_get_assets.return_value = {
            "record_id": "20397958",
            "metadata_filename": "map-icon-metadata.csv",
        }
        dm = DataManager(str(self.plugin_dir))
        png_dir = dm.cache_dir / "map-icon-png"
        png_dir.mkdir(parents=True)
        (png_dir / "00e8059e.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)
        dm._write_cached_record_id("20397958")

        info = dm.get_cache_info()
        self.assertEqual(info["icons_count"], 1)
        self.assertEqual(info["zenodo_record_id"], "20397958")
        self.assertEqual(info["zenodo_latest_record_id"], "20397958")
        self.assertIn("cache_dir", info)

    def test_check_dependencies_structure(self):
        dm = DataManager(str(self.plugin_dir))
        deps = dm.check_dependencies()
        self.assertIn("urllib", deps)
        self.assertIn("zipfile", deps)
        self.assertTrue(deps["urllib"])
        self.assertTrue(deps["zipfile"])

    @patch("map_icons.data_manager.urlopen")
    def test_download_file_success(self, mock_urlopen):
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
