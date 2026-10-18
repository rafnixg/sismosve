# Copyright (C) 2025-2026 Rafnix Guzman (@rafnixg).
# SPDX-License-Identifier: AGPL-3.0-only
# Additional author-attribution term under section 7(b): see repository-root NOTICE.
"""
Inicialización del módulo app
"""

# Importación lazy para evitar problemas de configuración durante testing/CI
def get_app():
    """Obtener la instancia de la aplicación FastAPI"""
    from .main import app
    return app

__all__ = ["get_app"]
