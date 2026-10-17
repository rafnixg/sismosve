#!/usr/bin/env python3
"""
Test simple para verificar que la aplicación funciona
"""
import os
import sys
import tempfile

# Configurar logging para test
os.environ['LOG_FILE'] = os.path.join(tempfile.gettempdir(), 'test_sismos_api.log')

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
