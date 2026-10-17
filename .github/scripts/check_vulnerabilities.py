"""Keep every finding visible and block publication on HIGH/CRITICAL findings."""
import json
import os
import sys
from collections import Counter
from pathlib import Path


def summarize(report):
    if report.get('SchemaVersion') != 2 or report.get('ArtifactType') != 'container_image':
        raise ValueError('Expected a Trivy container image report (schema 2)')
    results = report.get('Results')
    if not isinstance(results, list) or not results:
        raise ValueError('Missing scan results; refusing to treat an empty report as a clean scan')
    counts = Counter()
    for result in results:
        for vulnerability in result.get('Vulnerabilities') or []:
            severity = vulnerability.get('Severity', 'UNKNOWN')
            if severity not in {'UNKNOWN', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'}:
                raise ValueError('Unexpected vulnerability severity')
            counts[severity] += 1
    return counts


if __name__ == '__main__':
    try:
        counts = summarize(json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')))
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise SystemExit(f'Invalid vulnerability report: {error}') from error
    summary = '\n'.join(['## Container vulnerability scan', '', '| Severity | Findings |', '|---|---:|'] + [
        f'| {severity} | {counts[severity]} |'
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN']
    ]) + '\n'
    print(summary)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with Path(os.environ['GITHUB_STEP_SUMMARY']).open('a', encoding='utf-8') as output:
            output.write(summary)
    sys.exit(1 if counts['HIGH'] or counts['CRITICAL'] else 0)
