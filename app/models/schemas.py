"""
Modelos de datos para la aplicación de sismos
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    """Coordenadas geográficas"""

    longitude: float = Field(..., description="Longitud")
    latitude: float = Field(..., description="Latitud")


class Geometry(BaseModel):
    """Geometría del punto geográfico"""

    type: str = Field(default="Point", description="Tipo de geometría")
    coordinates: List[float] = Field(..., description="Coordenadas [lng, lat]")
    marcador: Optional[str] = Field(None, description="Tipo de marcador")


class SismoProperties(BaseModel):
    """Propiedades de un sismo"""

    depth: str = Field(..., description="Profundidad del sismo")
    value: str = Field(..., description="Magnitud del sismo")
    addressFormatted: str = Field(..., description="Dirección formateada")
    time: str = Field(..., description="Hora del sismo")
    country: str = Field(..., description="País")
    date: str = Field(..., description="Fecha del sismo")
    lat: str = Field(..., description="Latitud como string")
    long: str = Field(..., description="Longitud como string")


class Sismo(BaseModel):
    """Modelo de un sismo"""

    type: str = Field(default="Sismo", description="Tipo de feature")
    geometry: Geometry = Field(..., description="Geometría del sismo")
    properties: SismoProperties = Field(..., description="Propiedades del sismo")


class SismosCollection(BaseModel):
    """Colección de sismos"""

    type: str = Field(default="sismos", description="Tipo de colección")
    features: List[Sismo] = Field(..., description="Lista de sismos")


class FunvisisProperties(BaseModel):
    """Propiedades originales de FUNVISIS"""

    phoneFormatted: str
    phone: str
    address: str
    city: str
    country: str
    postalCode: str
    state: str
    lat: str
    long: str


class FunvisisGeometry(BaseModel):
    """Geometría original de FUNVISIS"""

    type: str
    coordinates: List[float]
    marcador: str


class FunvisisFeature(BaseModel):
    """Feature original de FUNVISIS"""

    type: str
    geometry: FunvisisGeometry
    properties: FunvisisProperties


class FunvisisCollection(BaseModel):
    """Colección original de FUNVISIS"""

    type: str
    features: List[FunvisisFeature]


class SismosStats(BaseModel):
    """Estadísticas de sismos"""

    total_sismos: int = Field(..., description="Total de sismos")
    magnitud_minima: float = Field(..., description="Magnitud mínima")
    magnitud_maxima: float = Field(..., description="Magnitud máxima")
    magnitud_promedio: float = Field(..., description="Magnitud promedio")
    ultimo_sismo: Optional[dict] = Field(
        None, description="Información del último sismo"
    )
    ultima_actualizacion: datetime = Field(
        ..., description="Timestamp de última actualización"
    )


class ApiResponse(BaseModel):
    """Respuesta estándar de la API"""

    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo")
    data: Optional[dict] = Field(None, description="Datos de respuesta")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Timestamp de la respuesta"
    )
