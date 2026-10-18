# Copyright (C) 2025-2026 Rafnix Guzman (@rafnixg).
# SPDX-License-Identifier: AGPL-3.0-only
# Additional author-attribution term under section 7(b): see repository-root NOTICE.
"""Synchronize release metadata with VERSION; no third-party dependencies."""
import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NUMERIC = r'(?:0|[1-9][0-9]*)'
IDENTIFIER = rf'(?:{NUMERIC}|[0-9]*[A-Za-z-][0-9A-Za-z-]*)'
PATTERN = rf'{NUMERIC}\.{NUMERIC}\.{NUMERIC}(?:-{IDENTIFIER}(?:\.{IDENTIFIER})*)?'


def validate_version(version):
    if len(version) > 127 or not re.fullmatch(PATTERN, version):
        raise ValueError('Use MAJOR.MINOR.PATCH or MAJOR.MINOR.PATCH-prerelease; no build metadata')
    return version


def synchronized_files(version, root):
    files = {'VERSION': version + '\n'}
    for name in ['frontend/package.json', 'frontend/package-lock.json']:
        data = json.loads((root / name).read_text(encoding='utf-8'))
        data['version'] = version
        if name.endswith('package-lock.json'):
            data['packages']['']['version'] = version
        files[name] = json.dumps(data, indent=2, ensure_ascii=False) + '\n'

    replacements = {
        'Dockerfile': (r'^ARG APP_VERSION=.*$', 'ARG APP_VERSION=' + version),
        'README.md': (r'^\*\*Versión del código: `[^`]+`\*\*', f'**Versión del código: `{version}`**'),
        'static/llms.txt': (r'^Versión: .*$', 'Versión: ' + version),
    }
    for name, (pattern, replacement) in replacements.items():
        text = (root / name).read_text(encoding='utf-8')
        files[name], count = re.subn(pattern, lambda _: replacement, text, flags=re.MULTILINE)
        if count != 1:
            raise ValueError(f'{name}: expected exactly one version field, found {count}')
    return files


def check_version(expected_version=None, root=ROOT):
    version = validate_version((root / 'VERSION').read_text(encoding='ascii').strip())
    if expected_version is not None and version != expected_version:
        raise ValueError(f'Tag version {expected_version} does not match VERSION ({version})')
    stale = [name for name, expected in synchronized_files(version, root).items()
             if (root / name).read_text(encoding='utf-8') != expected]
    if stale:
        raise ValueError('Version metadata out of sync: ' + ', '.join(stale)
                         + '; run python .github/scripts/project_version.py --set ' + version)
    if not re.search(r'^## \[' + re.escape(version) + r'\] - ',
                     (root / 'CHANGELOG.md').read_text(encoding='utf-8'), re.MULTILINE):
        raise ValueError(f'CHANGELOG.md: missing entry for {version}')
    return version


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    options = parser.add_mutually_exclusive_group(required=True)
    options.add_argument('--check', action='store_true')
    options.add_argument('--set', metavar='VERSION')
    args = parser.parse_args()
    try:
        if args.set:
            version = validate_version(args.set)
            for name, text in synchronized_files(version, ROOT).items():
                (ROOT / name).write_text(text, encoding='utf-8', newline='\n')
            print(f'Synchronized {version}. Update CHANGELOG.md before running --check.')
        else:
            print('Version metadata consistent: ' + check_version())
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
