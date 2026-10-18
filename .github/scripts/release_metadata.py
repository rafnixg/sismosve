# Copyright (C) 2025-2026 Rafnix Guzman (@rafnixg).
# SPDX-License-Identifier: AGPL-3.0-only
# Additional author-attribution term under section 7(b): see repository-root NOTICE.
"""Validate the pushed version tag before any registry or release write."""
import os
import re
from pathlib import Path

from project_version import check_version, validate_version


def metadata(tag, repository):
    if not tag.startswith('v'):
        raise ValueError('Use vMAJOR.MINOR.PATCH or vMAJOR.MINOR.PATCH-prerelease; no build metadata')
    validate_version(tag[1:])
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise ValueError('Invalid GitHub repository')
    return {
        'image': 'ghcr.io/' + repository.lower(),
        'tag': tag,
        'version': tag[1:],
        'prerelease': str('-' in tag).lower(),
    }


if __name__ == '__main__':
    if os.environ.get('GITHUB_EVENT_NAME') != 'push' or os.environ.get('GITHUB_REF_TYPE') != 'tag':
        raise SystemExit('Docker releases require a pushed version tag')
    try:
        values = metadata(os.environ['GITHUB_REF_NAME'], os.environ['GITHUB_REPOSITORY'])
        check_version(expected_version=values['version'])
    except (ValueError, OSError, KeyError) as error:
        raise SystemExit(str(error)) from error
    with Path(os.environ['GITHUB_OUTPUT']).open('a', encoding='utf-8') as output:
        for key, value in values.items():
            output.write(f'{key}={value}\n')
