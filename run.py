#!/usr/bin/env python3
"""
Script para ejecutar la aplicación SismosVE
"""
import sys
import subprocess
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def install_dependencies():
    """Instala las dependencias necesarias"""
    try:
        logger.info("Instalando dependencias...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )
        logger.info("Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al instalar dependencias: {e}")
        return False


def run_app(host="0.0.0.0", port=8000, reload=True):
    """Ejecuta la aplicación FastAPI"""
    try:
        logger.info(f"Iniciando aplicación en http://{host}:{port}")

        # Importar uvicorn y ejecutar
        import uvicorn

        uvicorn.run(
            "app.main:app", host=host, port=port, reload=reload, log_level="info"
        )
    except ImportError:
        logger.error(
            "uvicorn no está instalado. Ejecutando instalación de dependencias..."
        )
        if install_dependencies():
            import uvicorn

            uvicorn.run(
                "app.main:app", host=host, port=port, reload=reload, log_level="info"
            )
    except Exception as e:
        logger.error(f"Error al ejecutar la aplicación: {e}")


def main():
    """Función principal"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "install":
            install_dependencies()
        elif command == "dev":
            run_app(host="127.0.0.1", port=8000, reload=True)
        elif command == "prod":
            run_app(host="0.0.0.0", port=8000, reload=False)
        else:
            print("Uso: python run.py [install|dev|prod]")
            print("  install: Instala dependencias")
            print("  dev: Ejecuta en modo desarrollo (localhost:8000)")
            print("  prod: Ejecuta en modo producción (0.0.0.0:8000)")
    else:
        # Modo por defecto: desarrollo
        run_app(host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
