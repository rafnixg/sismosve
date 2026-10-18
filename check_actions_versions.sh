#!/usr/bin/env bash
# Copyright (C) 2025-2026 Rafnix Guzman (@rafnixg).
# SPDX-License-Identifier: AGPL-3.0-only
# Additional author-attribution term under section 7(b): see repository-root NOTICE.
# Audit the actual files rather than printing a hard-coded list of versions.
set -euo pipefail
cd -- "$(dirname -- "$0")"
python .github/scripts/check_workflows.py
zizmor --offline --no-config --strict-collection .github/workflows
