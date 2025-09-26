#!/usr/bin/env python3
"""
Script para mantener actualizado el archivo de sismos de FUNVISIS
Descarga los datos cada 5 minutos y actualiza el archivo local
"""

import json
import time
import os
import shutil
import glob
from datetime import datetime
import logging
import requests

class SismosUpdater:
    def __init__(self):
        self.url = "http://www.funvisis.gob.ve/maravilla.json"
        self.output_file = "sismosve.json"
        self.log_file = "updater.log"
        self.update_interval = 300  # 5 minutos en segundos
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def download_data(self):
        """Descarga los datos de sismos desde FUNVISIS"""
        try:
            self.logger.info("Descargando datos de FUNVISIS...")
            
            # Configurar headers para evitar problemas de CORS
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
            
            response = requests.get(self.url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            self.logger.info(f"Datos descargados exitosamente. {len(data.get('features', []))} sismos encontrados")
            
            return data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error al descargar datos: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Error al decodificar JSON: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error inesperado: {e}")
            return None
    
    def save_data(self, data):
        """Guarda los datos en el archivo local"""
        try:
            # Crear backup del archivo anterior si existe
            if os.path.exists(self.output_file):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{self.output_file}.backup_{timestamp}"
                
                # Crear backup con timestamp único
                try:
                    os.rename(self.output_file, backup_name)
                    self.logger.info(f"Backup creado: {backup_name}")
                except OSError as e:
                    # Si falla el rename, intentar copiar
                    shutil.copy2(self.output_file, backup_name)
                    os.remove(self.output_file)
                    self.logger.info(f"Backup creado (copiado): {backup_name}")
                
                # Limpiar backups antiguos (mantener solo los últimos 5)
                self.cleanup_old_backups()
            
            # Guardar los nuevos datos
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Datos guardados en {self.output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al guardar datos: {e}")
            return False
    
    def cleanup_old_backups(self, max_backups=5):
        """Elimina backups antiguos, manteniendo solo los más recientes"""
        try:
            backup_pattern = f"{self.output_file}.backup_*"
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
            self.logger.warning(f"Error al limpiar backups antiguos: {e}")
    
    def get_file_stats(self, data):
        """Obtiene estadísticas de los datos"""
        if not data or 'features' not in data:
            return "Sin datos válidos"
        
        features = data['features']
        total = len(features)
        
        if total == 0:
            return "No hay sismos registrados"
        
        # Obtener magnitudes
        magnitudes = []
        for feature in features:
            try:
                mag = float(feature['properties'].get('phone', 0))
                magnitudes.append(mag)
            except (ValueError, TypeError):
                pass
        
        if magnitudes:
            max_mag = max(magnitudes)
            min_mag = min(magnitudes)
            avg_mag = sum(magnitudes) / len(magnitudes)
            
            return f"Total: {total} sismos | Magnitud: {min_mag:.1f}-{max_mag:.1f} (promedio: {avg_mag:.1f})"
        
        return f"Total: {total} sismos"
    
    def run_once(self):
        """Ejecuta una actualización única"""
        self.logger.info("=" * 50)
        self.logger.info("Iniciando actualización de datos...")
        
        data = self.download_data()
        
        if data is not None:
            if self.save_data(data):
                stats = self.get_file_stats(data)
                self.logger.info(f"Actualización completada: {stats}")
                return True
            else:
                self.logger.error("Fallo al guardar los datos")
                return False
        else:
            self.logger.error("No se pudieron obtener los datos")
            return False
    
    def run_continuous(self):
        """Ejecuta el updater continuamente cada 5 minutos"""
        self.logger.info("Iniciando SismosUpdater en modo continuo")
        self.logger.info(f"Actualizando cada {self.update_interval} segundos ({self.update_interval//60} minutos)")
        self.logger.info(f"URL: {self.url}")
        self.logger.info(f"Archivo de salida: {self.output_file}")
        
        # Ejecutar primera actualización inmediatamente
        self.run_once()
        
        try:
            while True:
                self.logger.info(f"Esperando {self.update_interval} segundos hasta la próxima actualización...")
                time.sleep(self.update_interval)
                self.run_once()
                
        except KeyboardInterrupt:
            self.logger.info("Updater detenido por el usuario")
        except Exception as e:
            self.logger.error(f"Error crítico: {e}")

def main():
    import sys
    
    updater = SismosUpdater()
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "once":
            print("Ejecutando actualización única...")
            updater.run_once()
            return
        elif mode == "continuous":
            print("Iniciando modo continuo (Ctrl+C para detener)...")
            try:
                updater.run_continuous()
            except KeyboardInterrupt:
                print("\nUpdater detenido por el usuario")
            return
        else:
            print("Uso: python updater.py [once|continuous]")
            return
    
    # Modo interactivo
    print("SismosUpdater - Actualizador de datos de sismos FUNVISIS")
    print("=" * 55)
    print("1. Ejecutar una sola vez")
    print("2. Ejecutar continuamente cada 5 minutos")
    print("3. Salir")
    
    try:
        choice = input("Seleccione una opción (1-3): ").strip()
        
        if choice == "1":
            updater.run_once()
        elif choice == "2":
            print("\nPresiona Ctrl+C para detener el updater\n")
            updater.run_continuous()
        elif choice == "3":
            print("Saliendo...")
        else:
            print("Opción inválida")
            
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()