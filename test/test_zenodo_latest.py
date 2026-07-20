# coding=utf-8
"""
Live checks against the latest Zenodo release concept DOI.

Scheduled CI runs them weekly so a new Zenodo upload that breaks expected
filenames or metadata columns will fail the job.

"""
from __future__ import annotations

import csv
import importlib.util
import io
import os
import sys
import types
import unittest
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
RUN_LIVE = os.environ.get("RUN_ZENODO_LIVE_TESTS", "").strip() == "1"


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
    _USER_AGENT,
    get_zenodo_assets,
    resolve_latest_zenodo_assets,
)


@unittest.skipUnless(
    RUN_LIVE,
    "Set RUN_ZENODO_LIVE_TESTS=1 to hit the live Zenodo API",
)
class TestZenodoLatestLive(unittest.TestCase):
    """Resolve assets via the concept-record API that always points at latest."""

    def setUp(self):
        import map_icons.data_manager as dm_mod

        dm_mod._zenodo_assets = None

    def test_api_url_uses_concept_recid(self):
        self.assertIn(str(config.ZENODO_CONCEPT_RECID), config.ZENODO_API_LATEST_URL)
        self.assertEqual(config.ZENODO_DOI, config.ZENODO_CONCEPT_DOI)

    def test_resolve_latest_zenodo_assets_live(self):
        assets = resolve_latest_zenodo_assets()
        self.assertIsNotNone(
            assets,
            "Could not resolve latest Zenodo assets from "
            f"{config.ZENODO_API_LATEST_URL}",
        )
        self.assertTrue(str(assets["record_id"]).strip())
        self.assertTrue(assets["png_zip_url"])
        self.assertTrue(assets["svg_zip_url"])
        self.assertTrue(assets["metadata_csv_url"])
        self.assertEqual(assets["metadata_filename"], config.ZENODO_METADATA_CSV_NAME)
        for name, url in (
            (config.ZENODO_PNG_ZIP_NAME, assets["png_zip_url"]),
            (config.ZENODO_SVG_ZIP_NAME, assets["svg_zip_url"]),
            (config.ZENODO_METADATA_CSV_NAME, assets["metadata_csv_url"]),
        ):
            self.assertIn(name, url, f"Expected {name} in download URL {url}")

    def test_latest_metadata_csv_headers(self):
        assets = get_zenodo_assets(force_refresh=True)
        self.assertIsNotNone(assets)
        request = Request(
            assets["metadata_csv_url"],
            headers={"User-Agent": _USER_AGENT},
        )
        with urlopen(request, timeout=60) as response:
            chunk = response.read(8192).decode("utf-8-sig", errors="replace")
        header_line = chunk.splitlines()[0]
        headers = next(csv.reader(io.StringIO(header_line)))
        headers = [h.strip() for h in headers]
        for expected in config.METADATA_CSV_HEADERS:
            self.assertIn(
                expected,
                headers,
                f"Latest Zenodo metadata CSV is missing column {expected!r}. "
                f"Found: {headers}",
            )


if __name__ == "__main__":
    unittest.main()
