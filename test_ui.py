"""Server-rendered SEO and frontend integration regressions."""
import json
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
