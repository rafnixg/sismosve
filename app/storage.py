# Copyright (C) 2025-2026 Rafnix Guzman (@rafnixg).
# SPDX-License-Identifier: AGPL-3.0-only
# Additional author-attribution term under section 7(b): see repository-root NOTICE.
"""Persistent JSON storage shared by the API and standalone updater."""

import json
import os
import tempfile
from pathlib import Path
from typing import Optional

from .models.schemas import FunvisisCollection, SismosCollection

PROJECT_DIR = Path(__file__).resolve().parent.parent


def get_data_file() -> Path:
    """Use a stable path, independent of the process working directory."""
    configured = os.getenv("DATA_FILE")
    return Path(configured).expanduser().resolve() if configured else PROJECT_DIR / "data" / "sismosve.json"


def validate_data(data: dict) -> None:
    if data.get("type") == "FeatureCollection":
        FunvisisCollection(**data)
    else:
        SismosCollection(**data)


def initialize_data_file(data_file: Path, seed_file: Optional[Path] = None) -> Path:
    """Seed missing storage once; never replace an existing file at startup."""
    data_file = Path(data_file)
    data_file.parent.mkdir(parents=True, exist_ok=True)
    if not data_file.exists():
        seed = seed_file if seed_file is not None else PROJECT_DIR / "sismosve.json"
        payload = Path(seed).read_bytes()
        validate_data(json.loads(payload))
        try:
            # Exclusive creation also protects a file created by another starter.
            with data_file.open("xb") as output:
                output.write(payload)
        except FileExistsError:
            pass

    try:
        validate_data(json.loads(data_file.read_text(encoding="utf-8")))
    except (ValueError, OSError, TypeError, AttributeError) as error:
        raise RuntimeError(
            f"El JSON existente en {data_file} no es válido o no se puede leer; "
            "se conserva sin reemplazar. Restaura un respaldo válido."
        ) from error
    if not os.access(data_file, os.W_OK) or not os.access(data_file.parent, os.W_OK):
        raise PermissionError(
            f"El usuario del servicio necesita escritura en {data_file} y "
            f"{data_file.parent}. Revisa los permisos del volumen."
        )
    return data_file


def write_json_atomically(data_file: Path, data: dict) -> None:
    """Readers see either the old or the complete new JSON, never a partial write."""
    data_file = Path(data_file)
    data_file.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=data_file.parent,
            prefix=f".{data_file.name}.", suffix=".tmp", delete=False,
        ) as output:
            temporary = Path(output.name)
            json.dump(data, output, indent=2, ensure_ascii=False)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, data_file)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
