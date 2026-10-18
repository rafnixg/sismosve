#!/usr/bin/env python3
# Copyright (C) 2025-2026 Rafnix Guzman (@rafnixg).
# SPDX-License-Identifier: AGPL-3.0-only
# Additional author-attribution term under section 7(b): see repository-root NOTICE.
"""
Test simple para verificar que la aplicación funciona
"""
import os
import sys
import tempfile
from io import BytesIO

# Configurar logging para test
os.environ['LOG_FILE'] = os.path.join(tempfile.gettempdir(), 'test_sismos_api.log')

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_container_health_probe_rejects_unhealthy_http_200(monkeypatch):
    from app import healthcheck

    for status, expected in [('healthy', 0), ('unhealthy', 1), ('error', 1)]:
        body = ('{"status": "' + status + '"}').encode()
        monkeypatch.setattr(healthcheck, 'urlopen', lambda *args, **kwargs: BytesIO(body))
        assert healthcheck.main() == expected


def test_container_health_probe_fails_on_invalid_response_or_network_error(monkeypatch):
    from app import healthcheck

    monkeypatch.setattr(healthcheck, 'urlopen', lambda *args, **kwargs: BytesIO(b'invalid json'))
    assert healthcheck.main() == 1

    def timeout(*args, **kwargs):
        raise TimeoutError('Service unavailable')

    monkeypatch.setattr(healthcheck, 'urlopen', timeout)
    assert healthcheck.main() == 1


def test_health_endpoint():
    """Test del endpoint de health check"""
    try:
        from app.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get('/api/health')
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'status' in data, "Response missing 'status' field"
        assert data['status'] == 'healthy', f"Expected healthy status, got {data.get('status')}"
        
        print('✅ Health check passed')
        return None
        
    except Exception as e:
        print(f'❌ Health check failed: {e}')
        raise

def test_main_endpoint():
    """Test del endpoint principal"""
    try:
        from app.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get('/')
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert 'text/html' in response.headers.get('content-type', ''), "Expected HTML response"
        
        print('✅ Main endpoint test passed')
        return None
        
    except Exception as e:
        print(f'❌ Main endpoint test failed: {e}')
        raise

if __name__ == '__main__':
    print('🧪 Running SismosVE tests...')
    
    test_health_endpoint()
    test_main_endpoint()
    print('🎉 All tests passed!')
