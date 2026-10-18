"""Regression checks for the release boundary, credentials and scan failure policy.

Run from the repository root with Python + PyYAML. No Docker daemon is used.
"""
import json
import re
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from check_vulnerabilities import summarize
from release_metadata import metadata
from project_version import check_version


ROOT = Path(__file__).resolve().parents[2]


def workflow(name):
    # YAML 1.1 treats the Actions key `on` as a boolean; BaseLoader preserves it.
    return yaml.load((ROOT / '.github/workflows' / name).read_text(encoding='utf-8'), Loader=yaml.BaseLoader)


class WorkflowPolicy(unittest.TestCase):
    def test_only_version_tag_push_can_reach_docker_build(self):
        release = workflow('release.yml')
        self.assertEqual(release['on'], {'push': {'tags': ['v*']}})
        docker = workflow('docker-build.yml')
        self.assertEqual(set(docker['on']), {'workflow_call'})
        self.assertEqual(docker['jobs']['build-and-push']['if'],
                         "github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')")
        callers = []
        builds = []
        for file in (ROOT / '.github/workflows').glob('*.yml'):
            for job in workflow(file.name)['jobs'].values():
                if 'docker-build.yml' in job.get('uses', ''):
                    callers.append(file.name)
                for step in job.get('steps', []):
                    if step.get('uses', '').startswith('docker/build-push-action@'):
                        builds.append(file.name)
                    if re.search(r'\bdocker\s+(?:build\b|buildx\s+build\b|compose\s+build\b)', step.get('run', '')):
                        self.fail(f'Unexpected inline image build in {file.name}')
        self.assertEqual(callers, ['release.yml'])
        self.assertEqual(builds, ['docker-build.yml'])
        self.assertEqual(set(release['jobs']['image']['needs']), {'validate', 'checks'})
        self.assertEqual(set(workflow('ci.yml')['on']), {'push', 'pull_request', 'workflow_call'})

    def test_release_waits_for_scanned_image_and_latest_is_promoted_after_scan(self):
        jobs = workflow('docker-build.yml')['jobs']
        self.assertEqual(jobs['security-scan']['needs'], 'build-and-push')
        self.assertEqual(set(jobs['promote-latest']['needs']), {'build-and-push', 'security-scan'})
        self.assertEqual(jobs['promote-latest']['if'], '${{ !inputs.prerelease }}')
        build = next(s for s in jobs['build-and-push']['steps'] if s.get('id') == 'build')
        self.assertNotIn(':latest', build['with']['tags'])
        self.assertIn('steps.build.outputs.digest', jobs['build-and-push']['outputs']['image'])
        self.assertIn('image', workflow('release.yml')['jobs']['create-release']['needs'])

    def test_scan_includes_both_architectures_and_enforces_gate(self):
        job = workflow('container-scan.yml')['jobs']['scan']
        self.assertEqual(set(job['strategy']['matrix']['arch']), {'amd64', 'arm64'})
        scan = next(s for s in job['steps'] if s.get('id') == 'scan')
        self.assertEqual(scan['with']['ignore-unfixed'], 'false')
        self.assertEqual(scan['with']['image-ref'], '${{ inputs.image }}')
        self.assertEqual(job['steps'][-1]['run'], 'python .github/scripts/check_vulnerabilities.py trivy.json')
        self.assertNotIn('continue-on-error', job['steps'][-1])

    def test_external_actions_are_pinned_and_checkout_does_not_keep_credentials(self):
        for file in (ROOT / '.github/workflows').glob('*.yml'):
            data = workflow(file.name)
            self.assertEqual(data['permissions'], {'contents': 'read'}, file.name)
            self.assertNotIn('pull_request_target', data['on'])
            for job in data['jobs'].values():
                for step in job.get('steps', []):
                    action = step.get('uses', '')
                    if action:
                        self.assertRegex(action, r'^[\w./-]+@[a-f0-9]{40}$', file.name)
                    if action.startswith('actions/checkout@'):
                        self.assertEqual(step['with']['persist-credentials'], 'false')
        maintenance = workflow('maintenance.yml')
        self.assertNotIn('cleanup-packages', maintenance['jobs'])
        self.assertNotIn('issues: write', (ROOT / '.github/workflows/maintenance.yml').read_text())

    def test_ci_always_checks_dependency_changes_and_keeps_vite_manifest(self):
        ci = workflow('ci.yml')
        self.assertNotIn('paths-ignore', ci['on']['push'])
        self.assertNotIn('paths-ignore', ci['on']['pull_request'])
        upload = next(s for s in ci['jobs']['frontend']['steps']
                      if s.get('uses', '').startswith('actions/upload-artifact@'))
        self.assertEqual(upload['with']['include-hidden-files'], 'true')
        self.assertIn('3.14', ci['jobs']['test']['strategy']['matrix']['python-version'])

    def test_stable_and_prerelease_metadata(self):
        for tag, prerelease in [('v0.2.1', 'false'), ('v2.0.0-rc.1', 'true'),
                                ('v1.0.0-preview', 'true'), ('v1.0.0-0', 'true')]:
            with self.subTest(tag=tag):
                result = metadata(tag, 'Rafnixg/SismosVE')
                self.assertEqual(result['prerelease'], prerelease)
                self.assertEqual(result['image'], 'ghcr.io/rafnixg/sismosve')
                self.assertEqual(result['version'], tag[1:])

    def test_project_metadata_and_docker_build_use_the_same_version(self):
        version = check_version()
        build = next(s for s in workflow('docker-build.yml')['jobs']['build-and-push']['steps']
                     if s.get('id') == 'build')
        self.assertEqual(build['with']['build-args'], 'APP_VERSION=${{ inputs.version }}')
        self.assertIn('org.opencontainers.image.version=${{ inputs.version }}', build['with']['labels'])
        self.assertEqual(metadata('v' + version, 'rafnixg/sismosve')['version'], version)

    def test_drift_in_frontend_or_documentation_blocks_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ['VERSION', 'frontend/package.json', 'frontend/package-lock.json',
                         'Dockerfile', 'README.md', 'static/llms.txt', 'CHANGELOG.md']:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            for name in ['frontend/package.json', 'frontend/package-lock.json', 'Dockerfile',
                         'README.md', 'static/llms.txt']:
                with self.subTest(file=name):
                    original = (root / name).read_text(encoding='utf-8')
                    version = (root / 'VERSION').read_text().strip()
                    (root / name).write_text(original.replace(version, '99.99.99', 1), encoding='utf-8')
                    with self.assertRaisesRegex(ValueError, re.escape(name)):
                        check_version(root=root)
                    (root / name).write_text(original, encoding='utf-8')
            (root / 'CHANGELOG.md').write_text('# No version entry\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'CHANGELOG.md'):
                check_version(root=root)

    def test_release_tag_mismatch_writes_no_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'outputs'
            result = subprocess.run([sys.executable, str(ROOT / '.github/scripts/release_metadata.py')],
                                    cwd=ROOT, capture_output=True, text=True,
                                    env={**os.environ, 'GITHUB_EVENT_NAME': 'push', 'GITHUB_REF_TYPE': 'tag',
                                         'GITHUB_REF_NAME': 'v99.99.99', 'GITHUB_REPOSITORY': 'rafnixg/sismosve',
                                         'GITHUB_OUTPUT': str(output)})
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('does not match VERSION', result.stderr)
            self.assertFalse(output.exists())

    def test_malformed_or_unsafe_versions_are_rejected(self):
        for tag in ['main', 'v.0.1.0', 'v1', 'v01.0.0', 'v1.0.0-01', 'v1.0.0-',
                    'v1.0.0+meta', 'v1.0.0\nimage=other', 'v1.0.0;id', 'v1.0.0-$(id)',
                    'v1.0.0-' + 'a' * 128]:
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                metadata(tag, 'rafnixg/sismosve')

    def test_gate_preserves_unfixed_high_and_critical_findings(self):
        report = {'SchemaVersion': 2, 'ArtifactType': 'container_image', 'Results': [
            {'Vulnerabilities': [{'Severity': 'LOW'}, {'Severity': 'HIGH', 'FixedVersion': ''},
                                 {'Severity': 'CRITICAL', 'FixedVersion': '2.0'}]},
            {'Vulnerabilities': None},
        ]}
        counts = summarize(json.loads(json.dumps(report)))
        self.assertEqual(counts['HIGH'], 1)
        self.assertEqual(counts['CRITICAL'], 1)
        self.assertEqual(counts['LOW'], 1)

    def test_incomplete_scan_is_not_treated_as_clean(self):
        for report in [{}, {'SchemaVersion': 2, 'ArtifactType': 'container_image'},
                       {'SchemaVersion': 2, 'ArtifactType': 'container_image', 'Results': []}]:
            with self.subTest(report=report), self.assertRaises(ValueError):
                summarize(report)
        clean = {'SchemaVersion': 2, 'ArtifactType': 'container_image', 'Results': [{'Vulnerabilities': None}]}
        self.assertFalse(summarize(clean))


if __name__ == '__main__':
    unittest.main(verbosity=2)
