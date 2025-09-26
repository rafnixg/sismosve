"""
Servicio para manejar datos de sismos
"""

import json
import os
import shutil
import glob
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

from ..models.schemas import (
    SismosCollection,
    FunvisisCollection,
    SismosStats,
    Sismo,
    SismoProperties,
    Geometry,
)


class SismosService:
    """Servicio para manejar operaciones de sismos"""

    def __init__(self, data_file: str = "sismosve.json"):
        self.data_file = data_file
        self.logger = logging.getLogger(__name__)

    def load_sismos(self) -> Optional[SismosCollection]:
        """Carga los sismos desde el archivo JSON"""
        try:
            if not os.path.exists(self.data_file):
                self.logger.warning(f"Archivo {self.data_file} no existe")
                return None

            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Si los datos están en formato FUNVISIS, transformarlos
            if data.get("type") == "FeatureCollection":
                funvisis_data = FunvisisCollection(**data)
                return self.transform_funvisis_to_sismos(funvisis_data)
            else:
                return SismosCollection(**data)

        except Exception as e:
            self.logger.error(f"Error al cargar sismos: {e}")
            return None

    def save_sismos(self, sismos: SismosCollection, create_backup: bool = True) -> bool:
        """Guarda los sismos en el archivo JSON"""
        try:
            # Crear backup si es necesario
            if create_backup and os.path.exists(self.data_file):
                self._create_backup()

            # Guardar datos
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(sismos.dict(), f, indent=2, ensure_ascii=False)

            self.logger.info(f"Sismos guardados en {self.data_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error al guardar sismos: {e}")
            return False

    def transform_funvisis_to_sismos(
        self, funvisis_data: FunvisisCollection
    ) -> SismosCollection:
        """Transforma datos de FUNVISIS al formato de sismos"""
        sismos = []

        for feature in funvisis_data.features:
            # Transformar propiedades
            properties = SismoProperties(
                depth=feature.properties.phoneFormatted or feature.properties.state,
                value=feature.properties.phone,
                addressFormatted=feature.properties.address,
                time=feature.properties.city,
                country=feature.properties.country,
                date=feature.properties.postalCode,
                lat=feature.properties.lat,
                long=feature.properties.long,
            )

            # Transformar geometría
            geometry = Geometry(
                type=feature.geometry.type,
                coordinates=feature.geometry.coordinates,
                marcador=feature.geometry.marcador,
            )

            # Crear sismo
            sismo = Sismo(type="Sismo", geometry=geometry, properties=properties)

            sismos.append(sismo)

        return SismosCollection(type="sismos", features=sismos)

    def get_sismos_stats(self, sismos: SismosCollection) -> SismosStats:
        """Calcula estadísticas de los sismos"""
        if not sismos or not sismos.features:
            return SismosStats(
                total_sismos=0,
                magnitud_minima=0.0,
                magnitud_maxima=0.0,
                magnitud_promedio=0.0,
                ultimo_sismo=None,
                ultima_actualizacion=datetime.now(),
            )

        # Obtener magnitudes
        magnitudes = []
        for sismo in sismos.features:
            try:
                mag = float(sismo.properties.value)
                magnitudes.append(mag)
            except (ValueError, TypeError):
                pass

        if not magnitudes:
            magnitudes = [0.0]

        # Obtener último sismo
        ultimo_sismo = self._get_latest_earthquake(sismos.features)

        return SismosStats(
            total_sismos=len(sismos.features),
            magnitud_minima=min(magnitudes),
            magnitud_maxima=max(magnitudes),
            magnitud_promedio=sum(magnitudes) / len(magnitudes),
            ultimo_sismo=ultimo_sismo.dict() if ultimo_sismo else None,
            ultima_actualizacion=datetime.now(),
        )

    def get_sismos_by_magnitude(
        self, sismos: SismosCollection, min_magnitude: float
    ) -> List[Sismo]:
        """Filtra sismos por magnitud mínima"""
        filtered = []
        for sismo in sismos.features:
            try:
                mag = float(sismo.properties.value)
                if mag >= min_magnitude:
                    filtered.append(sismo)
            except (ValueError, TypeError):
                continue
        return filtered

    def get_recent_sismos(
        self, sismos: SismosCollection, limit: int = 10
    ) -> List[Sismo]:
        """Obtiene los sismos más recientes"""
        # Ordenar por fecha/hora (más reciente primero)
        sorted_sismos = sorted(
            sismos.features,
            key=lambda s: self._parse_datetime(s.properties.date, s.properties.time),
            reverse=True,
        )
        return sorted_sismos[:limit]

    def _create_backup(self):
        """Crea un backup del archivo de datos"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{self.data_file}.backup_{timestamp}"

            shutil.copy2(self.data_file, backup_name)
            self.logger.info(f"Backup creado: {backup_name}")

            # Limpiar backups antiguos
            self._cleanup_old_backups()

        except Exception as e:
            self.logger.warning(f"Error al crear backup: {e}")

    def _cleanup_old_backups(self, max_backups: int = 5):
        """Elimina backups antiguos"""
        try:
            backup_pattern = f"{self.data_file}.backup_*"
            backup_files = glob.glob(backup_pattern)

            if len(backup_files) > max_backups:
                # Ordenar por fecha de modificación (más antiguo primero)
                backup_files.sort(key=os.path.getmtime)

                # Eliminar los más antiguos
                files_to_delete = backup_files[:-max_backups]
                for file_to_delete in files_to_delete:
                    os.remove(file_to_delete)
                    self.logger.info(f"Backup antiguo eliminado: {file_to_delete}")

        except Exception as e:
            self.logger.warning(f"Error al limpiar backups: {e}")

    def _get_latest_earthquake(self, sismos: List[Sismo]) -> Optional[Sismo]:
        """Obtiene el sismo más reciente"""
        if not sismos:
            return None

        return max(
            sismos,
            key=lambda s: self._parse_datetime(s.properties.date, s.properties.time),
        )

    def _parse_datetime(self, date_str: str, time_str: str) -> datetime:
        """Convierte fecha y hora string a datetime"""
        try:
            # Formato esperado: DD-MM-YYYY y HH:MM
            day, month, year = date_str.split("-")
            hours, minutes = time_str.split(":")
            return datetime(int(year), int(month), int(day), int(hours), int(minutes))
        except:
            return datetime.min
