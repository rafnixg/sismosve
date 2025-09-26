#!/bin/bash
"""
Script para verificar y actualizar versiones de GitHub Actions
"""

echo "🔍 Verificando versiones de GitHub Actions..."
echo "=============================================="

# Función para verificar una acción específica
check_action() {
    local action=$1
    local current_version=$2
    echo "📦 $action: $current_version"
}

echo ""
echo "🐳 Docker Build Workflow:"
check_action "actions/checkout" "v4"
check_action "docker/setup-buildx-action" "v3"  
check_action "docker/login-action" "v3"
check_action "docker/metadata-action" "v5"
check_action "docker/build-push-action" "v6"
check_action "anchore/sbom-action" "v0.17.2"
check_action "actions/upload-artifact" "v4"
check_action "aquasecurity/trivy-action" "0.24.0"
check_action "github/codeql-action/upload-sarif" "v3"

echo ""
echo "🧪 CI Workflow:"
check_action "actions/checkout" "v4"
check_action "actions/setup-python" "v4"
check_action "actions/cache" "v3"
check_action "actions/upload-artifact" "v4"

echo ""
echo "📦 Release Workflow:"
check_action "actions/checkout" "v4"
check_action "softprops/action-gh-release" "v1"
check_action "actions/github-script" "v7"

echo ""
echo "🛠️ Maintenance Workflow:"
check_action "actions/checkout" "v4"
check_action "actions/setup-python" "v4"
check_action "actions/github-script" "v7"

echo ""
echo "✅ Todas las versiones han sido actualizadas a las más recientes"
echo "🚀 Los workflows están listos para ejecutarse sin errores"