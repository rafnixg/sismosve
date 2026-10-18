# Copyright (C) 2025-2026 Rafnix Guzman (@rafnixg).
# SPDX-License-Identifier: AGPL-3.0-only
# Additional author-attribution term under section 7(b): see repository-root NOTICE.
"""Data safety and persistence regressions, without accessing FUNVISIS."""
import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from app import storage
from app.models.schemas import SismosCollection
from app.services.sismos_service import SismosService
from app.services.updater_service import UpdaterService
from updater import SismosUpdater


def test_api_and_standalone_updater_share_configured_path(tmp_path, monkeypatch):
    target = tmp_path / "persistent" / "sismosve.json"
    monkeypatch.setenv("DATA_FILE", str(target))
    monkeypatch.chdir(tmp_path)
    assert SismosService().data_file == str(target)
    assert SismosUpdater().output_file == str(target)


def test_default_path_does_not_depend_on_working_directory(tmp_path, monkeypatch):
    monkeypatch.delenv("DATA_FILE", raising=False)
    monkeypatch.chdir(tmp_path)
    assert storage.get_data_file() == storage.PROJECT_DIR / "data" / "sismosve.json"


def test_initialization_seeds_only_missing_file(tmp_path):
    seed = storage.PROJECT_DIR / "sismosve.json"
    target = tmp_path / "data" / "sismosve.json"
    storage.initialize_data_file(target, seed)
    assert target.read_bytes() == seed.read_bytes()
    # A restored file must survive repeated startups even when the image seed differs.
    target.write_text('{"type":"sismos", "features": []}', encoding="utf-8")
    before, modified = target.read_bytes(), target.stat().st_mtime_ns
    storage.initialize_data_file(target, seed)
    assert target.read_bytes() == before
    assert target.stat().st_mtime_ns == modified


@pytest.mark.parametrize("payload", ['{"broken":', '[]', '{"features":42}'])
def test_corrupt_existing_data_is_never_replaced(tmp_path, payload):
    target = tmp_path / "sismosve.json"
    target.write_text(payload, encoding="utf-8")
    with pytest.raises(RuntimeError, match="se conserva sin reemplazar"):
        storage.initialize_data_file(target)
    assert target.read_text(encoding="utf-8") == payload


def test_invalid_seed_does_not_create_data_file(tmp_path):
    seed, target = tmp_path / "seed.json", tmp_path / "data.json"
    seed.write_text('{"bad":"seed"}', encoding="utf-8")
    with pytest.raises(ValueError):
        storage.initialize_data_file(target, seed)
    assert not target.exists()


def test_unwritable_volume_fails_without_fallback(tmp_path, monkeypatch):
    target = tmp_path / "data.json"
    target.write_text('{"type":"sismos","features":[]}', encoding="utf-8")
    monkeypatch.setattr(storage.os, "access", lambda *args: False)
    with pytest.raises(PermissionError, match="permisos del volumen"):
        storage.initialize_data_file(target)


def test_service_writes_and_backups_stay_in_data_directory(tmp_path):
    target = tmp_path / "volume" / "sismosve.json"
    storage.initialize_data_file(target)
    old = target.read_bytes()
    service = SismosService(str(target))
    assert service.save_sismos(SismosCollection(type="sismos", features=[]))
    backups = list(target.parent.glob("sismosve.json.backup_*"))
    assert len(backups) == 1
    assert backups[0].read_bytes() == old
    # A new service instance reads exactly what the previous one saved.
    assert SismosService(str(target)).load_sismos().features == []
    for _ in range(7):
        assert service.save_sismos(SismosCollection(type="sismos", features=[]))
    assert len(list(target.parent.glob("sismosve.json.backup_*"))) == 5


def test_failed_atomic_replace_keeps_previous_json(tmp_path, monkeypatch):
    target = tmp_path / "data.json"
    storage.initialize_data_file(target)
    before = target.read_bytes()

    def fail_replace(*args):
        raise OSError("simulated storage failure")

    monkeypatch.setattr(storage.os, "replace", fail_replace)
    assert not SismosService(str(target)).save_sismos(SismosCollection(type="sismos", features=[]))
    assert target.read_bytes() == before
    assert not list(tmp_path.glob("*.tmp"))


def test_standalone_updater_rejects_invalid_data_and_writes_atomically(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "volume" / "sismosve.json"
    storage.initialize_data_file(target)
    before = target.read_bytes()
    updater = SismosUpdater(str(target))
    assert not updater.save_data({"bad": "download"})
    assert target.read_bytes() == before
    assert updater.save_data({"type": "sismos", "features": []})
    assert json.loads(target.read_text())["features"] == []
    assert next(target.parent.glob("*.backup_*")).read_bytes() == before
    monkeypatch.setattr(storage.os, "replace", Mock(side_effect=OSError("disk error")))
    assert not updater.save_data({"type": "sismos", "features": []})
    assert json.loads(target.read_text())["features"] == []


def test_scheduler_preserves_existing_json_on_startup(tmp_path):
    target = tmp_path / "data.json"
    storage.initialize_data_file(target)
    before = target.read_bytes()

    async def run():
        updater = UpdaterService(SismosService(str(target)))
        updater.scheduler = Mock()
        updater.update_sismos_data = AsyncMock(return_value=True)
        await updater.start_scheduler()
        updater.update_sismos_data.assert_not_awaited()
        updater.scheduler.add_job.assert_called_once()
        await updater.stop_scheduler()

    asyncio.run(run())
    assert target.read_bytes() == before


def test_scheduler_fetches_when_no_json_exists(tmp_path):
    async def run():
        updater = UpdaterService(SismosService(str(tmp_path / "missing.json")))
        updater.scheduler = Mock()
        updater.update_sismos_data = AsyncMock(return_value=True)
        await updater.start_scheduler()
        updater.update_sismos_data.assert_awaited_once()
        await updater.stop_scheduler()

    asyncio.run(run())


def test_standalone_funvisis_format_survives_startup_and_api_read(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    raw = {"type": "FeatureCollection", "features": [{
        "type": "Feature", "geometry": {"type": "Point", "coordinates": [-66, 8], "marcador": "marker"},
        "properties": {"phoneFormatted": "10 km", "phone": "3.2", "address": "Caracas",
                       "city": "13:05", "country": "Venezuela", "postalCode": "17-10-2026",
                       "state": "10 km", "lat": "8", "long": "-66"},
    }]}
    target = tmp_path / "volume" / "sismosve.json"
    assert SismosUpdater(str(target)).save_data(raw)
    before = target.read_bytes()
    storage.initialize_data_file(target)
    assert target.read_bytes() == before
    loaded = SismosService(str(target)).load_sismos()
    assert loaded.features[0].properties.value == "3.2"
    assert loaded.features[0].properties.addressFormatted == "Caracas"


def test_failed_funvisis_download_keeps_persistent_records(tmp_path):
    target = tmp_path / "data.json"
    storage.initialize_data_file(target)
    before = target.read_bytes()

    async def run():
        updater = UpdaterService(SismosService(str(target)))
        updater._download_funvisis_data = AsyncMock(return_value=None)
        assert await updater.update_sismos_data() is False

    asyncio.run(run())
    assert target.read_bytes() == before
