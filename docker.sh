#!/bin/bash
"""
Scripts de Docker para SismosVE
Facilita la construcción y ejecución del contenedor
"""

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}🐳 Scripts de Docker para SismosVE${NC}"
    echo -e "${BLUE}=================================${NC}"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo -e "  ${GREEN}build${NC}     - Construir la imagen Docker"
    echo -e "  ${GREEN}run${NC}       - Ejecutar contenedor en modo desarrollo"
    echo -e "  ${GREEN}prod${NC}      - Ejecutar con docker-compose (producción)"
    echo -e "  ${GREEN}stop${NC}      - Detener todos los contenedores"
    echo -e "  ${GREEN}clean${NC}     - Limpiar imágenes y contenedores"
    echo -e "  ${GREEN}logs${NC}      - Ver logs del contenedor"
    echo -e "  ${GREEN}shell${NC}     - Acceder al shell del contenedor"
    echo -e "  ${GREEN}health${NC}    - Verificar estado de salud"
    echo -e "  ${GREEN}rebuild${NC}   - Reconstruir imagen desde cero"
    echo ""
}

# Función para construir la imagen
build_image() {
    echo -e "${YELLOW}🔨 Construyendo imagen Docker...${NC}"
    docker build -t sismosve:latest .
    echo -e "${GREEN}✅ Imagen construida exitosamente${NC}"
}

# Función para ejecutar en desarrollo
run_dev() {
    echo -e "${YELLOW}🚀 Ejecutando SismosVE en modo desarrollo...${NC}"
    docker run -d \
        --name sismosve-dev \
        -p 8000:8000 \
        -v "sismove-data:/app/data" \
        -v "$(pwd)/logs:/app/logs" \
        --restart unless-stopped \
        sismosve:latest
    
    echo -e "${GREEN}✅ Contenedor iniciado${NC}"
    echo -e "${BLUE}🌐 Aplicación disponible en: http://localhost:8000${NC}"
    echo -e "${BLUE}📚 API Docs en: http://localhost:8000/docs${NC}"
}

# Función para ejecutar en producción
run_prod() {
    echo -e "${YELLOW}🚀 Ejecutando SismosVE en modo producción...${NC}"
    docker-compose up -d
    echo -e "${GREEN}✅ Servicios iniciados con docker-compose${NC}"
    echo -e "${BLUE}🌐 Aplicación disponible en: http://localhost:8000${NC}"
}

# Función para detener contenedores
stop_containers() {
    echo -e "${YELLOW}🛑 Deteniendo contenedores...${NC}"
    docker stop sismosve-dev 2>/dev/null || true
    docker-compose down 2>/dev/null || true
    echo -e "${GREEN}✅ Contenedores detenidos${NC}"
}

# Función para limpiar
clean_docker() {
    echo -e "${YELLOW}🧹 Limpiando Docker...${NC}"
    stop_containers
    docker rm sismosve-dev 2>/dev/null || true
    docker rmi sismosve:latest 2>/dev/null || true
    docker system prune -f
    echo -e "${GREEN}✅ Limpieza completada${NC}"
}

# Función para ver logs
show_logs() {
    echo -e "${YELLOW}📋 Mostrando logs...${NC}"
    if docker ps --format '{{.Names}}' | grep -q sismosve-dev; then
        docker logs -f sismosve-dev
    elif docker-compose ps | grep -q sismosve; then
        docker-compose logs -f sismosve
    else
        echo -e "${RED}❌ No hay contenedores de SismosVE ejecutándose${NC}"
    fi
}

# Función para acceder al shell
access_shell() {
    echo -e "${YELLOW}🐚 Accediendo al shell del contenedor...${NC}"
    if docker ps --format '{{.Names}}' | grep -q sismosve-dev; then
        docker exec -it sismosve-dev /bin/bash
    elif docker-compose ps | grep -q sismosve; then
        docker-compose exec sismosve /bin/bash
    else
        echo -e "${RED}❌ No hay contenedores de SismosVE ejecutándose${NC}"
    fi
}

# Función para verificar salud
check_health() {
    echo -e "${YELLOW}🏥 Verificando estado de salud...${NC}"
    if curl -f http://localhost:8000/api/health 2>/dev/null; then
        echo -e "${GREEN}✅ Aplicación saludable${NC}"
    else
        echo -e "${RED}❌ Aplicación no responde${NC}"
    fi
}

# Función para reconstruir
rebuild_image() {
    echo -e "${YELLOW}🔄 Reconstruyendo imagen desde cero...${NC}"
    stop_containers
    docker rmi sismosve:latest 2>/dev/null || true
    docker build --no-cache -t sismosve:latest .
    echo -e "${GREEN}✅ Imagen reconstruida exitosamente${NC}"
}

# Procesamiento de argumentos
case "${1:-help}" in
    "build")
        build_image
        ;;
    "run")
        build_image
        run_dev
        ;;
    "prod")
        build_image
        run_prod
        ;;
    "stop")
        stop_containers
        ;;
    "clean")
        clean_docker
        ;;
    "logs")
        show_logs
        ;;
    "shell")
        access_shell
        ;;
    "health")
        check_health
        ;;
    "rebuild")
        rebuild_image
        ;;
    "help"|*)
        show_help
        ;;
esac