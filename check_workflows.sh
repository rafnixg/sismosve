#!/bin/bash
"""
Script para verificar el estado de los workflows de GitHub Actions
"""

echo "🔍 Verificando estado de GitHub Actions workflows..."
echo "=================================================="

# Función para mostrar el estado de un workflow
check_workflow() {
    local workflow_name=$1
    local workflow_file=$2
    echo "📋 $workflow_name ($workflow_file)"
    
    if [ -f ".github/workflows/$workflow_file" ]; then
        echo "   ✅ Archivo existe"
        
        # Verificar sintaxis YAML básica
        if python -c "import yaml; yaml.safe_load(open('.github/workflows/$workflow_file'))" 2>/dev/null; then
            echo "   ✅ Sintaxis YAML válida"
        else
            echo "   ❌ Error de sintaxis YAML"
        fi
    else
        echo "   ❌ Archivo no encontrado"
    fi
    echo ""
}

echo "Workflows configurados:"
check_workflow "Docker Build & Push" "docker-build.yml"
check_workflow "CI/CD Pipeline" "ci.yml"
check_workflow "Release Automation" "release.yml"
check_workflow "Maintenance" "maintenance.yml"

echo "Dependabot configuración:"
if [ -f ".github/dependabot.yml" ]; then
    echo "   ✅ Dependabot configurado"
else
    echo "   ❌ Dependabot no configurado"
fi

echo ""
echo "🧪 Testing local:"
if [ -f "test_app.py" ]; then
    echo "   ✅ Script de test disponible"
else
    echo "   ❌ Script de test no encontrado"
fi

if [ -f "pytest.ini" ]; then
    echo "   ✅ Configuración pytest disponible"
else
    echo "   ❌ Configuración pytest no encontrada"
fi

echo ""
echo "🐳 Docker setup:"
if [ -f "Dockerfile" ]; then
    echo "   ✅ Dockerfile disponible"
else
    echo "   ❌ Dockerfile no encontrado"
fi

if [ -f "docker-compose.yml" ]; then
    echo "   ✅ Docker Compose disponible"
else
    echo "   ❌ Docker Compose no encontrado"
fi

if [ -f "docker-entrypoint.sh" ]; then
    echo "   ✅ Docker entrypoint disponible"
else
    echo "   ❌ Docker entrypoint no encontrado"
fi

echo ""
echo "✅ Verificación completa"
echo "🚀 Para ejecutar workflows: git push origin main"
echo "🏷️  Para crear release: git tag v1.0.0 && git push origin v1.0.0"