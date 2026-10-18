# Copyright (C) 2025-2026 Rafnix Guzman (@rafnixg).
# SPDX-License-Identifier: AGPL-3.0-only
# Additional author-attribution term under section 7(b): see repository-root NOTICE.
"""Server-rendered SEO and frontend integration regressions."""
import json
import hashlib
import re
from pathlib import Path
from xml.etree import ElementTree

from fastapi.testclient import TestClient
from app.main import app
from app.config import PUBLIC_URL
from app.version import __version__

client = TestClient(app)


def test_public_api_reports_the_project_version():
    expected = Path('VERSION').read_text(encoding='ascii').strip()
    assert __version__ == expected
    assert client.get('/openapi.json').json()['info']['version'] == expected
    assert client.get('/api/health').json()['version'] == expected


def test_license_and_notice_are_served_with_the_full_text():
    license_text = Path('LICENSE').read_text(encoding='utf-8')
    # SPDX's unmodified AGPL-3.0-only text, with normalized line endings.
    assert hashlib.sha256(license_text.encode()).hexdigest() == 'd8a6cc31abc16b6748c7a21f21611f5a1ec33f67d22ca23d7da1c19b95496bee'
    for url, file in [('/license', 'LICENSE'), ('/notice', 'NOTICE')]:
        response = client.get(url)
        assert response.status_code == 200
        assert response.headers['content-type'].startswith('text/plain')
        assert response.text.replace('\r\n', '\n') == Path(file).read_text(encoding='utf-8')
    notice = client.get('/notice').text
    assert 'section 7(b)' in notice and 'Rafnix Guzman (@rafnixg)' in notice
    assert 'does not change third-party license terms' in notice


def test_credit_and_legal_links_are_present_without_javascript():
    for url in ['/', '/static/docs/privacy.html', '/static/docs/terms.html']:
        html = client.get(url).text
        footer = re.search(r'<footer\b[^>]*>(.*?)</footer>', html, re.S).group(1)
        assert 'SismosVE - desarrollado originalmente por' in footer
        assert 'Rafnix Guzman (@rafnixg)' in footer
        assert 'href="https://github.com/rafnixg"' in footer
        assert 'sin garantía' in footer
        for link in ['/license', '/notice', '/source']:
            assert f'href="{link}"' in footer


def test_corresponding_source_offer_supports_forks(monkeypatch):
    monkeypatch.delenv('SOURCE_URL', raising=False)
    response = client.get('/source', follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['location'] == 'https://github.com/rafnixg/sismosve'
    fork_source = 'https://example.org/sismosve/archive/exact-commit.tar.gz'
    monkeypatch.setenv('SOURCE_URL', fork_source)
    response = client.get('/source', follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['location'] == fork_source


def test_licensing_is_consistent_across_public_metadata_and_terms():
    info = client.get('/openapi.json').json()['info']
    assert info['license']['url'] == PUBLIC_URL + '/license'
    assert 'section 7(b)' in info['license']['name']
    assert 'Rafnix Guzman (@rafnixg)' in info['description']
    terms = client.get('/static/docs/terms.html').text
    assert 'incluso comercialmente' in terms
    assert 'Uso comercial sin autorización previa' not in terms
    assert 'sección 13' in terms
    assert 'dominio público' not in terms
    licenses = client.get('/static/ui/third-party-licenses.txt')
    assert licenses.status_code == 200
    for name in ['svelte', 'leaflet', '@fontsource/source-sans-3']:
        assert name in licenses.text
    assert 'SIL OPEN FONT LICENSE' in licenses.text


def test_seo_is_available_without_javascript():
    response = client.get('/')
    assert response.status_code == 200
    html = response.text
    assert html.count('<h1>') == 1
    assert 'Sismos en Venezuela</h1>' in html
    for marker in ['<title>', 'name="description"', 'rel="canonical"',
                   'property="og:title"', 'name="twitter:card"']:
        assert html.count(marker) == 1
    assert f'rel="canonical" href="{PUBLIC_URL}/"' in html
    schema = json.loads(re.search(r'application/ld\+json">(.*?)</script>', html, re.S).group(1))
    assert schema['url'] == PUBLIC_URL + '/'
    assert schema['inLanguage'] == 'es-VE'
    assert 'FUNVISIS' in html
    assert 'localhost' not in html
    assert 'no-store' in response.headers['cache-control']


def test_report_and_legal_links_are_server_rendered():
    html = client.get('/').text
    assert 'href="https://encuesta.funvisis.gob.ve/" target="_blank" rel="noopener noreferrer"' in html
    for url in ['/static/docs/privacy.html', '/static/docs/terms.html', '/api/sismos']:
        assert f'href="{url}"' in html
        assert client.get(url).status_code == 200


def test_crawlers_and_assets():
    robots = client.get('/robots.txt').text
    assert f'Sitemap: {PUBLIC_URL}/sitemap.xml' in robots
    assert '{{' not in robots
    sitemap = client.get('/sitemap.xml')
    root = ElementTree.fromstring(sitemap.text)
    for loc in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
        assert loc.text.startswith(PUBLIC_URL + '/')
    for url in ['/humans.txt', '/llms.txt', '/static/manifest.json',
                '/static/images/favicon.svg', '/static/images/sismos-venezuela-preview.png']:
        assert client.get(url).status_code == 200
    manifest = client.get('/static/manifest.json').json()
    for icon in manifest['icons']:
        assert client.get(icon['src']).status_code == 200


def test_compiled_frontend_is_referenced_when_built():
    manifest_path = Path('static/ui/.vite/manifest.json')
    assert manifest_path.exists(), 'Build frontend before running integration tests'
    entry = json.loads(manifest_path.read_text())['src/main.ts']
    html = client.get('/').text
    for asset in [entry['file'], *entry.get('css', [])]:
        assert '/static/ui/' + asset in html
        assert client.get('/static/ui/' + asset).status_code == 200
