"""
Configuración de la aplicación SismosVE
"""

import logging
import os
from pathlib import Path
from contextlib import asynccontextmanager

from .services import SismosService, UpdaterService
from .storage import get_data_file, initialize_data_file


def setup_logging():
    """Configurar logging con fallback en caso de errores de permisos"""
    handlers = []
    
    # Siempre incluir console output
    console_handler = logging.StreamHandler()
    handlers.append(console_handler)
    
    # Intentar configurar file logging
    log_file = os.getenv("LOG_FILE")
    if not log_file:
        # Detectar entorno y configurar path apropiado
        if os.path.exists("/app"):
            log_file = "/app/logs/sismos_api.log"
        else:
            log_file = "sismos_api.log"
    
    try:
        # Intentar crear directorio de logs
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # Agregar file handler si es posible
        file_handler = logging.FileHandler(log_file)
        handlers.append(file_handler)
        print(f"📝 Logging configurado: {log_file}")
    except (PermissionError, OSError) as e:
        print(f"⚠️  No se pudo configurar file logging: {e}")
        print("📝 Usando solo console logging")
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
        force=True  # Sobrescribir configuración existente
    )


# Configurar rutas
BASE_DIR = Path(__file__).parent.parent
PUBLIC_URL = os.getenv("PUBLIC_URL", "https://sismosve.rafnixg.dev").rstrip("/")
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
DATA_DIR = get_data_file().parent

# Servicios globales
sismos_service = SismosService()
updater_service = UpdaterService(sismos_service, update_interval=300)  # 5 minutos

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("Iniciando aplicación SismosVE...")
    try:
        initialize_data_file(Path(sismos_service.data_file))
        await updater_service.start_scheduler()
        logger.info("Aplicación iniciada correctamente")
    except Exception as e:
        logger.error("Error al iniciar aplicación: %s", e)
        raise

    yield

    # Shutdown
    logger.info("Cerrando aplicación...")
    await updater_service.stop_scheduler()
    logger.info("Aplicación cerrada")
