#!/usr/bin/env bash
# Validate workflow syntax, release policy and security. Requires the documented tools.
set -euo pipefail
cd -- "$(dirname -- "$0")"
python .github/scripts/check_workflows.py
actionlint
zizmor --offline --no-config --strict-collection .github/workflows
