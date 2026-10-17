"""Validate the pushed version tag before any registry or release write."""
import os
import re
from pathlib import Path


def metadata(tag, repository):
    # SemVer identifiers, excluding '+' (not supported in Docker tag names).
    numeric = r'(?:0|[1-9][0-9]*)'
    identifier = rf'(?:{numeric}|[0-9]*[A-Za-z-][0-9A-Za-z-]*)'
    pattern = rf'v{numeric}\.{numeric}\.{numeric}(?:-{identifier}(?:\.{identifier})*)?'
    if len(tag) > 128 or not re.fullmatch(pattern, tag):
        raise ValueError('Use vMAJOR.MINOR.PATCH or vMAJOR.MINOR.PATCH-prerelease; no build metadata')
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
    except ValueError as error:
        raise SystemExit(str(error)) from error
    with Path(os.environ['GITHUB_OUTPUT']).open('a', encoding='utf-8') as output:
        for key, value in values.items():
            output.write(f'{key}={value}\n')
