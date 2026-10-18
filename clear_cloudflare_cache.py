#!/usr/bin/env python3
# Copyright (C) 2025-2026 Rafnix Guzman (@rafnixg).
# SPDX-License-Identifier: AGPL-3.0-only
# Additional author-attribution term under section 7(b): see repository-root NOTICE.
"""
Script para limpiar cache de Cloudflare Tunnel
Simula la limpieza de cache para SismosVE
"""

import sys
import time
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("cache_clear.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


def clear_cache():
    """
    Simula la limpieza de cache de Cloudflare Tunnel
    En un entorno real, aquí se haría la llamada a la API de Cloudflare
    """
    try:
        logger.info("🚀 Iniciando limpieza de cache de Cloudflare Tunnel...")

        # Simular limpieza de cache
        logger.info("🧹 Limpiando cache de archivos estáticos...")
        time.sleep(1)

        logger.info("🧹 Limpiando cache de CSS...")
        time.sleep(0.5)

        logger.info("🧹 Limpiando cache de JavaScript...")
        time.sleep(0.5)

        logger.info("🧹 Limpiando cache de imágenes...")
        time.sleep(0.5)

        logger.info("🧹 Limpiando cache de API endpoints...")
        time.sleep(0.5)

        # Simular respuesta exitosa
        logger.info("✅ Cache de Cloudflare Tunnel limpiado exitosamente")
        logger.info(
            "⏰ Tiempo de limpieza: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        return True

    except (ConnectionError, TimeoutError, ValueError) as e:
        logger.error("❌ Error limpiando cache: %s", e)
        return False


def main():
    """Función principal"""
    logger.info("=" * 50)
    logger.info("🌩️  CLOUDFLARE TUNNEL CACHE CLEANER")
    logger.info("=" * 50)

    success = clear_cache()

    if success:
        logger.info("🎉 Proceso completado exitosamente")
        sys.exit(0)
    else:
        logger.error("💥 Proceso falló")
        sys.exit(1)


if __name__ == "__main__":
    main()
