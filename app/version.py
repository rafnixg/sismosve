# Copyright (C) 2025-2026 Rafnix Guzman (@rafnixg).
# SPDX-License-Identifier: AGPL-3.0-only
# Additional author-attribution term under section 7(b): see repository-root NOTICE.
"""Application version shared by the API and release tooling."""
from pathlib import Path

__version__ = (Path(__file__).resolve().parents[1] / 'VERSION').read_text(encoding='ascii').strip()
