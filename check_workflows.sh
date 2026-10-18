#!/usr/bin/env bash
# Copyright (C) 2025-2026 Rafnix Guzman (@rafnixg).
# SPDX-License-Identifier: AGPL-3.0-only
# Additional author-attribution term under section 7(b): see repository-root NOTICE.
# Validate workflow syntax, release policy and security. Requires the documented tools.
set -euo pipefail
cd -- "$(dirname -- "$0")"
python .github/scripts/check_workflows.py
actionlint
zizmor --offline --no-config --strict-collection .github/workflows
