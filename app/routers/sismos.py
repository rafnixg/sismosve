"""
Router para endpoints de sismos
"""

import logging
from fastapi import APIRouter, HTTPException

from ..models import SismosCollection, SismosStats
from ..config import sismos_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Sismos"])


@router.get("/sismos", response_model=SismosCollection)
async def get_sismos():
    """Obtiene todos los sismos"""
    try:
        sismos = sismos_service.load_sismos()
        if not sismos:
            raise HTTPException(
                status_code=404, detail="No se encontraron datos de sismos"
            )
        return sismos
    except Exception as e:
        logger.error("Error al obtener sismos: %s", e)
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/sismos/stats", response_model=SismosStats)
async def get_sismos_stats():
    """Obtiene estadísticas de los sismos"""
    try:
        sismos = sismos_service.load_sismos()
        if not sismos:
            raise HTTPException(
                status_code=404, detail="No se encontraron datos de sismos"
            )

        stats = sismos_service.get_sismos_stats(sismos)
        return stats
    except Exception as e:
        logger.error("Error al obtener estadísticas: %s", e)
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/sismos/recent")
async def get_recent_sismos(limit: int = 10):
    """Obtiene los sismos más recientes"""
    try:
        if limit < 1 or limit > 50:
            raise HTTPException(
                status_code=400, detail="El límite debe estar entre 1 y 50"
            )

        sismos = sismos_service.load_sismos()
        if not sismos:
            raise HTTPException(
                status_code=404, detail="No se encontraron datos de sismos"
            )

        recent = sismos_service.get_recent_sismos(sismos, limit)
        return {"sismos": recent, "total": len(recent)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error al obtener sismos recientes: %s", e)
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/sismos/magnitude/{min_magnitude}")
async def get_sismos_by_magnitude(min_magnitude: float):
    """Obtiene sismos por magnitud mínima"""
    try:
        if min_magnitude < 0 or min_magnitude > 10:
            raise HTTPException(
                status_code=400, detail="La magnitud debe estar entre 0 y 10"
            )

        sismos = sismos_service.load_sismos()
        if not sismos:
            raise HTTPException(
                status_code=404, detail="No se encontraron datos de sismos"
            )

        filtered = sismos_service.get_sismos_by_magnitude(sismos, min_magnitude)
        return {
            "sismos": filtered,
            "total": len(filtered),
            "min_magnitude": min_magnitude,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error al filtrar sismos por magnitud: %s", e)
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/sismos/coordinates")
async def get_sismos_coordinates():
    """Obtiene solo las coordenadas y magnitudes para mapas"""
    try:
        sismos = sismos_service.load_sismos()
        if not sismos:
            raise HTTPException(
                status_code=404, detail="No se encontraron datos de sismos"
            )

        coordinates = []
        for feature in sismos.features:
            try:
                lat = float(feature.properties.lat)
                lng = float(feature.properties.long)
                magnitude = float(feature.properties.value)

                coordinates.append(
                    {
                        "lat": lat,
                        "lng": lng,
                        "magnitude": magnitude,
                        "location": feature.properties.addressFormatted,
                        "date": feature.properties.date,
                        "time": feature.properties.time,
                        "depth": feature.properties.depth,
                    }
                )
            except (ValueError, TypeError):
                continue

        return {"coordinates": coordinates, "total": len(coordinates)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error al obtener coordenadas: %s", e)
        raise HTTPException(status_code=500, detail="Error interno del servidor")