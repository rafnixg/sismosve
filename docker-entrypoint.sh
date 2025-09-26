#!/bin/bash
"""
Script de inicialización para contenedor
Asegura que los permisos sean correctos antes de iniciar la aplicación
"""

echo "🔧 Configurando permisos para SismosVE..."

# Crear directorio de logs si no existe
mkdir -p /app/logs

# Verificar si somos root o usuario sismosve
if [ "$(id -u)" = "0" ]; then
    echo "⚠️  Ejecutando como root, configurando permisos..."
    # Si somos root, asegurar que el usuario sismosve tenga permisos
    chown -R sismosve:sismosve /app
    chmod -R 755 /app
    chmod -R 777 /app/logs
    
    # Cambiar a usuario sismosve y ejecutar la aplicación
    echo "👤 Cambiando a usuario sismosve..."
    exec su-exec sismosve python run.py prod
else
    echo "👤 Ejecutando como usuario $(whoami)"
    # Si ya somos el usuario correcto, solo crear logs
    touch /app/logs/sismos_api.log 2>/dev/null || echo "📝 Usando logging por consola"
fi

echo "🚀 Iniciando aplicación SismosVE..."
exec python run.py prod