# Copyright (C) 2025-2026 Rafnix Guzman (@rafnixg).
# SPDX-License-Identifier: AGPL-3.0-only
# Additional author-attribution term under section 7(b): see repository-root NOTICE.
"""API tests read an isolated data snapshot instead of touching persistent data."""
import shutil

import pytest


@pytest.fixture(autouse=True)
def isolated_api_data(tmp_path, monkeypatch):
    from app.config import sismos_service
    from app.storage import PROJECT_DIR

    target = tmp_path / "api-data" / "sismosve.json"
    target.parent.mkdir()
    shutil.copyfile(PROJECT_DIR / "sismosve.json", target)
    monkeypatch.setattr(sismos_service, "data_file", str(target))
