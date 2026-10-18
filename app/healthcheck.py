# Copyright (C) 2025-2026 Rafnix Guzman (@rafnixg).
# SPDX-License-Identifier: AGPL-3.0-only
# Additional author-attribution term under section 7(b): see repository-root NOTICE.
"""Container health probe using the Python standard library."""
import json
import sys
from urllib.request import urlopen


def main():
    try:
        with urlopen('http://127.0.0.1:8000/api/health', timeout=5) as response:
            healthy = json.load(response).get('status') == 'healthy'
    except (OSError, ValueError):
        healthy = False
    return 0 if healthy else 1


if __name__ == '__main__':
    sys.exit(main())
