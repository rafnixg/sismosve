"""
Manejadores de excepciones para la aplicación
"""

import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from jinja2 import UndefinedError

logger = logging.getLogger(__name__)


async def not_found_handler(request: Request, exc: HTTPException):
    """Manejador personalizado para 404"""
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint no encontrado", "path": str(request.url.path)},
    )


async def jinja_undefined_handler(request: Request, exc: UndefinedError):
    """Manejador para errores de template Jinja2"""
    logger.error("Error de template en %s: %s", request.url.path, str(exc))
    return JSONResponse(
        status_code=500, 
        content={"detail": "Error en el template", "error": str(exc)}
    )


async def internal_error_handler(request: Request, exc: Exception):
    """Manejador personalizado para errores internos"""
    logger.error("Error interno en %s: %s", request.url.path, str(exc))
    return JSONResponse(
        status_code=500, content={"detail": "Error interno del servidor"}
    )