#!/bin/bash
# Copyright (C) 2025-2026 Rafnix Guzman (@rafnixg).
# SPDX-License-Identifier: AGPL-3.0-only
# Additional author-attribution term under section 7(b): see repository-root NOTICE.
"""
Script de limpieza automática para SismosVE
Elimina archivos temporales, logs y cachés
"""

echo "🧹 Iniciando limpieza del proyecto SismosVE..."
echo "=============================================="

# Cambiar al directorio del proyecto
cd "$(dirname "$0")"

# Limpiar logs
echo "📝 Limpiando archivos de log..."
rm -f *.log cache_clear.log sismos_api.log 2>/dev/null || true

# Limpiar caché de Python
echo "🐍 Limpiando caché de Python..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Limpiar archivos temporales
echo "🗑️ Limpiando archivos temporales..."
rm -f *.tmp *.temp .DS_Store Thumbs.db 2>/dev/null || true
find . -name "*~" -delete 2>/dev/null || true
find . -name "*.bak" -delete 2>/dev/null || true
find . -name "*.swp" -delete 2>/dev/null || true
find . -name "*.swo" -delete 2>/dev/null || true

# Limpiar backups antiguos de JSON (mantener solo el principal)
echo "💾 Limpiando backups antiguos..."
rm -f sismosve.json.backup* 2>/dev/null || true

# Verificar tamaño final
echo "=============================================="
echo "📊 Espacio liberado:"
du -sh . 2>/dev/null || echo "Limpieza completada"

echo "✅ Limpieza completada exitosamente"
echo "🚀 Proyecto listo para uso"