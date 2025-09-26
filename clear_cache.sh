#!/bin/bash
"""
Script de ejecución para limpiar cache de Cloudflare Tunnel
"""

echo "🌩️  Ejecutando limpieza de cache de Cloudflare Tunnel..."
echo "=================================================="

# Ejecutar el script de Python
python3 clear_cloudflare_cache.py

# Capturar el código de salida
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "=================================================="
    echo "✅ Limpieza de cache completada exitosamente"
    echo "🔄 Los cambios deberían ser visibles en unos minutos"
else
    echo "=================================================="
    echo "❌ Error en la limpieza de cache"
    echo "📝 Revisa el archivo cache_clear.log para más detalles"
fi

exit $exit_code