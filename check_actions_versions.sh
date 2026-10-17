#!/usr/bin/env bash
# Audit the actual files rather than printing a hard-coded list of versions.
set -euo pipefail
cd -- "$(dirname -- "$0")"
python .github/scripts/check_workflows.py
zizmor --offline --no-config --strict-collection .github/workflows
