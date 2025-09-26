"""
Inicialización del módulo app
"""

# Importación lazy para evitar problemas de configuración durante testing/CI
def get_app():
    """Obtener la instancia de la aplicación FastAPI"""
    from .main import app
    return app

__all__ = ["get_app"]
